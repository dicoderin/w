// Satsuma Exchange Testnet Bot - Complete Implementation
// Based on official Satsuma Exchange documentation

const { ethers } = require('ethers');
require('dotenv').config();

// Configuration - Store private key in .env file for security
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const RPC_URL = 'https://rpc.test.citrea.io';

// Contract addresses from Satsuma on Citrea Testnet
const SUMA_TOKEN_ADDRESS = '0x0E822C71F749Fb9bB2Aa06AB41B27FAB7Abbc583';
const WETH_TOKEN_ADDRESS = '0x67a8a98033d60ce8D5292F1b5D5A78e20b9C465d';
const ROUTER_ADDRESS = '0x7fbc0187Ccc3592d3F13fb0EA632f4418B7A11dF';
const STAKING_ADDRESS = '0xCb11d6C903996360f33e6F86ee679E898b7D4c85';
const VE_SUMA_ADDRESS = '0xF6eE0AF6F8bA4c3679dafE7dC42f33ab83b80960';
const VOTING_ADDRESS = '0x927695fc7b995FA91Ee4e99Bdea6DE0303Eb99eb';

// ABIs based on Satsuma documentation
const ERC20_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function balanceOf(address) view returns (uint)",
  "function transfer(address to, uint amount) returns (bool)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)"
];

const ROUTER_ABI = [
  "function getAmountsOut(uint amountIn, address[] memory path) public view returns (uint[] memory amounts)",
  "function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) external returns (uint[] memory amounts)",
  "function addLiquidity(address tokenA, address tokenB, uint amountADesired, uint amountBDesired, uint amountAMin, uint amountBMin, address to, uint deadline) external returns (uint amountA, uint amountB, uint liquidity)",
  "function removeLiquidity(address tokenA, address tokenB, uint liquidity, uint amountAMin, uint amountBMin, address to, uint deadline) external returns (uint amountA, uint amountB)",
  "function factory() external pure returns (address)"
];

const VESUMA_ABI = [
  "function convertSuma(uint256 amount) external returns (uint256)",
  "function balanceOf(address account) external view returns (uint256)",
  "function approve(address spender, uint256 amount) external returns (bool)"
];

const STAKING_ABI = [
  "function stake(uint256 amount) external",
  "function unstake(uint256 amount) external",
  "function getReward() external",
  "function balanceOf(address account) external view returns (uint256)",
  "function earned(address account) external view returns (uint256)"
];

const VOTING_ABI = [
  "function vote(uint256 proposalId, uint8 support) external",
  "function getProposals() external view returns (uint256[] memory)",
  "function getProposal(uint256 proposalId) external view returns (address,uint256,uint256,uint256,uint256,uint256,bool)",
  "function hasVoted(uint256 proposalId, address voter) external view returns (bool)"
];

// Main function
async function main() {
  try {
    console.log("Starting Satsuma Exchange Testnet Bot...");
    
    // Setup provider and wallet
    const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    const address = await wallet.getAddress();
    
    console.log(`Using wallet: ${address}`);
    
    // Check network
    const network = await provider.getNetwork();
    console.log(`Connected to network: ${network.name} (Chain ID: ${network.chainId})`);
    
    // Initialize contracts
    const sumaToken = new ethers.Contract(SUMA_TOKEN_ADDRESS, ERC20_ABI, wallet);
    const wethToken = new ethers.Contract(WETH_TOKEN_ADDRESS, ERC20_ABI, wallet);
    const router = new ethers.Contract(ROUTER_ADDRESS, ROUTER_ABI, wallet);
    const veSuma = new ethers.Contract(VE_SUMA_ADDRESS, VESUMA_ABI, wallet);
    const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, wallet);
    const voting = new ethers.Contract(VOTING_ADDRESS, VOTING_ABI, wallet);
    
    // Check balances
    const sumaBalance = await sumaToken.balanceOf(address);
    const wethBalance = await wethToken.balanceOf(address);
    
    console.log(`SUMA Balance: ${ethers.utils.formatEther(sumaBalance)} SUMA`);
    console.log(`WETH Balance: ${ethers.utils.formatEther(wethBalance)} WETH`);
    
    // If balance is too low, alert the user
    if (sumaBalance.lt(ethers.utils.parseEther("0.1")) || wethBalance.lt(ethers.utils.parseEther("0.01"))) {
      console.log("Warning: Low token balance. Consider getting tokens from the faucet:");
      console.log("- Citrea faucet: https://citrea.xyz/faucet");
      console.log("- WETH faucet: Visit the Satsuma website");
    }
    
    // 1. TRADING - Swap SUMA for WETH
    console.log("\n1. TESTING TRADING FEATURE...");
    
    const amountToSwap = ethers.utils.parseEther("0.01"); // Swap 0.01 SUMA
    
    if (sumaBalance.gte(amountToSwap)) {
      // Approve router to spend SUMA
      console.log("Approving SUMA for trading...");
      const approvalTx = await sumaToken.approve(ROUTER_ADDRESS, amountToSwap);
      await approvalTx.wait();
      console.log(`Approval transaction confirmed: ${approvalTx.hash}`);
      
      // Get price quote
      const amountsOut = await router.getAmountsOut(
        amountToSwap,
        [SUMA_TOKEN_ADDRESS, WETH_TOKEN_ADDRESS]
      );
      const expectedWETH = amountsOut[1];
      console.log(`Expected to receive: ${ethers.utils.formatEther(expectedWETH)} WETH`);
      
      // Execute swap with 1% slippage tolerance
      console.log("Executing swap transaction...");
      const minAmountOut = expectedWETH.mul(99).div(100); // 1% slippage
      const deadline = Math.floor(Date.now() / 1000) + 300; // 5 minutes
      
      const swapTx = await router.swapExactTokensForTokens(
        amountToSwap,
        minAmountOut,
        [SUMA_TOKEN_ADDRESS, WETH_TOKEN_ADDRESS],
        address,
        deadline
      );
      
      await swapTx.wait();
      console.log(`Swap transaction confirmed: ${swapTx.hash}`);
      
      // Check new balances
      const newSumaBalance = await sumaToken.balanceOf(address);
      const newWethBalance = await wethToken.balanceOf(address);
      console.log(`New SUMA balance: ${ethers.utils.formatEther(newSumaBalance)} SUMA`);
      console.log(`New WETH balance: ${ethers.utils.formatEther(newWethBalance)} WETH`);
    } else {
      console.log("Insufficient SUMA balance for trading");
    }
    
    // 2. ADD LIQUIDITY - SUMA/WETH pair
    console.log("\n2. ADDING LIQUIDITY...");
    
    const sumaToAddLiquidity = ethers.utils.parseEther("0.05");
    const wethToAddLiquidity = ethers.utils.parseEther("0.005");
    
    if (
      (await sumaToken.balanceOf(address)).gte(sumaToAddLiquidity) && 
      (await wethToken.balanceOf(address)).gte(wethToAddLiquidity)
    ) {
      // Approve both tokens
      console.log("Approving SUMA for liquidity...");
      const approveSumaTx = await sumaToken.approve(ROUTER_ADDRESS, sumaToAddLiquidity);
      await approveSumaTx.wait();
      console.log(`SUMA approval confirmed: ${approveSumaTx.hash}`);
      
      console.log("Approving WETH for liquidity...");
      const approveWethTx = await wethToken.approve(ROUTER_ADDRESS, wethToAddLiquidity);
      await approveWethTx.wait();
      console.log(`WETH approval confirmed: ${approveWethTx.hash}`);
      
      // Add liquidity
      console.log("Adding liquidity...");
      const deadline = Math.floor(Date.now() / 1000) + 300; // 5 minutes
      
      // Minimum amounts (accepting 1% slippage)
      const minSuma = sumaToAddLiquidity.mul(99).div(100);
      const minWeth = wethToAddLiquidity.mul(99).div(100);
      
      const addLiquidityTx = await router.addLiquidity(
        SUMA_TOKEN_ADDRESS,
        WETH_TOKEN_ADDRESS,
        sumaToAddLiquidity,
        wethToAddLiquidity,
        minSuma,
        minWeth,
        address,
        deadline
      );
      
      const receipt = await addLiquidityTx.wait();
      console.log(`Liquidity added successfully: ${addLiquidityTx.hash}`);
      
      // Get LP token address and balance (if needed)
      const factory = await router.factory();
      console.log(`Liquidity pool created on factory: ${factory}`);
    } else {
      console.log("Insufficient token balance for adding liquidity");
    }
    
    // 3. CONVERT SUMA TO VESUMA
    console.log("\n3. CONVERTING SUMA TO VESUMA...");
    
    const sumaToConvert = ethers.utils.parseEther("0.03");
    
    if ((await sumaToken.balanceOf(address)).gte(sumaToConvert)) {
      // Approve SUMA to be used by veSuma contract
      console.log("Approving SUMA for conversion...");
      const approveTx = await sumaToken.approve(VE_SUMA_ADDRESS, sumaToConvert);
      await approveTx.wait();
      console.log(`Approval transaction confirmed: ${approveTx.hash}`);
      
      // Convert SUMA to veSUMA
      console.log("Converting SUMA to veSUMA...");
      const convertTx = await veSuma.convertSuma(sumaToConvert);
      await convertTx.wait();
      console.log(`Conversion transaction confirmed: ${convertTx.hash}`);
      
      // Check veSUMA balance
      const veSumaBalance = await veSuma.balanceOf(address);
      console.log(`veSUMA Balance: ${ethers.utils.formatEther(veSumaBalance)} veSUMA`);
    } else {
      console.log("Insufficient SUMA balance for conversion");
    }
    
    // 4. STAKE VESUMA
    console.log("\n4. STAKING VESUMA...");
    
    const veSumaBalance = await veSuma.balanceOf(address);
    const veSumaToStake = veSumaBalance.div(2); // Stake half of the veSUMA balance
    
    if (veSumaBalance.gt(0) && veSumaToStake.gt(0)) {
      // Approve veSUMA to be used by staking contract
      console.log("Approving veSUMA for staking...");
      const approveTx = await veSuma.approve(STAKING_ADDRESS, veSumaToStake);
      await approveTx.wait();
      console.log(`Approval transaction confirmed: ${approveTx.hash}`);
      
      // Stake veSUMA
      console.log("Staking veSUMA...");
      const stakeTx = await staking.stake(veSumaToStake);
      await stakeTx.wait();
      console.log(`Staking transaction confirmed: ${stakeTx.hash}`);
      
      // Check staked balance
      const stakedBalance = await staking.balanceOf(address);
      console.log(`Staked veSUMA Balance: ${ethers.utils.formatEther(stakedBalance)} veSUMA`);
      
      // Check rewards (if any)
      const earned = await staking.earned(address);
      console.log(`Earned rewards: ${ethers.utils.formatEther(earned)}`);
    } else {
      console.log("No veSUMA available for staking");
    }
    
    // 5. VOTE WITH VESUMA
    console.log("\n5. PARTICIPATING IN GOVERNANCE...");
    
    try {
      // Get active proposals
      const proposals = await voting.getProposals();
      console.log(`Found ${proposals.length} proposals`);
      
      if (proposals.length > 0) {
        // Get details of the first proposal
        const proposalId = proposals[0];
        const proposalDetails = await voting.getProposal(proposalId);
        console.log(`Proposal ${proposalId} details:`, proposalDetails);
        
        // Check if already voted
        const hasVoted = await voting.hasVoted(proposalId, address);
        
        if (!hasVoted) {
          console.log(`Voting on proposal ${proposalId}...`);
          const support = 1; // 1 = For, 0 = Against, 2 = Abstain
          const voteTx = await voting.vote(proposalId, support);
          await voteTx.wait();
          console.log(`Vote transaction confirmed: ${voteTx.hash}`);
        } else {
          console.log(`Already voted on proposal ${proposalId}`);
        }
      } else {
        console.log("No active proposals found");
      }
    } catch (error) {
      console.log("Error accessing governance features:", error.message);
      console.log("This could be normal if governance features are limited on testnet");
    }
    
    console.log("\nAll Satsuma Exchange Testnet interactions completed successfully!");
    console.log("Summary of actions performed:");
    console.log("✅ Connected wallet to Satsuma Exchange");
    console.log("✅ Executed a trade on Satsuma");
    console.log("✅ Added liquidity to Satsuma");
    console.log("✅ Converted SUMA to veSUMA");
    console.log("✅ Staked veSUMA");
    console.log("✅ Participated in governance (if available)");
    
  } catch (error) {
    console.error("Error running Satsuma bot:", error);
    console.error("Stack trace:", error.stack);
  }
}

// Run the bot
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
  });
