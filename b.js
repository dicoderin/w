// Satsuma Exchange Testnet Bot - Complete Implementation
const { ethers } = require('ethers');
require('dotenv').config();

// Configuration
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const RPC_URL = 'https://rpc.test.citrea.io';

// Validate environment variables
if (!PRIVATE_KEY) {
  throw new Error("PRIVATE_KEY not found in .env file");
}
if (!RPC_URL) {
  throw new Error("RPC_URL not configured");
}

// Contract addresses (Citrea Testnet)
const SUMA_TOKEN_ADDRESS = '0x0E822C71F749Fb9bB2Aa06AB41B27FAB7Abbc583';
const WETH_TOKEN_ADDRESS = '0x67a8a98033d60ce8D5292F1b5D5A78e20b9C465d';
const ROUTER_ADDRESS = '0x7fbc0187Ccc3592d3F13fb0EA632f4418B7A11dF';
const STAKING_ADDRESS = '0xCb11d6C903996360f33e6F86ee679E898b7D4c85';
const VE_SUMA_ADDRESS = '0xF6eE0AF6F8bA4c3679dafE7dC42f33ab83b80960';
const VOTING_ADDRESS = '0x927695fc7b995FA91Ee4e99Bdea6DE0303Eb99eb';

// ABIs (optimized for required functions)
const ERC20_ABI = [
  "function balanceOf(address) view returns (uint)",
  "function approve(address spender, uint256 amount) returns (bool)"
];

const ROUTER_ABI = [
  "function getAmountsOut(uint amountIn, address[] memory path) view returns (uint[] memory amounts)",
  "function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) returns (uint[] memory amounts)",
  "function addLiquidity(address tokenA, address tokenB, uint amountADesired, uint amountBDesired, uint amountAMin, uint amountBMin, address to, uint deadline) returns (uint amountA, uint amountB, uint liquidity)",
  "function factory() view returns (address)"
];

const VESUMA_ABI = [
  "function convertSuma(uint256 amount) external",
  "function balanceOf(address account) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)"
];

const STAKING_ABI = [
  "function stake(uint256 amount) external",
  "function balanceOf(address account) view returns (uint256)",
  "function earned(address account) view returns (uint256)"
];

const VOTING_ABI = [
  "function vote(uint256 proposalId, uint8 support) external",
  "function getProposals() view returns (uint256[] memory)",
  "function getProposal(uint256 proposalId) view returns (tuple(address,uint256,uint256,uint256,uint256,uint256,bool))",
  "function hasVoted(uint256 proposalId, address voter) view returns (bool)"
];

async function main() {
  try {
    console.log("Starting Satsuma Exchange Testnet Bot...");
    
    // FIX: Use explicit network configuration
    const provider = new ethers.providers.StaticJsonRpcProvider(
      RPC_URL,
      {
        chainId: 1923,        // Citrea Testnet chain ID
        name: 'citrea-testnet'
      }
    );
    
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    const address = await wallet.getAddress();
    console.log(`Using wallet: ${address}`);
    
    // Initialize contracts
    const sumaToken = new ethers.Contract(SUMA_TOKEN_ADDRESS, ERC20_ABI, wallet);
    const wethToken = new ethers.Contract(WETH_TOKEN_ADDRESS, ERC20_ABI, wallet);
    const router = new ethers.Contract(ROUTER_ADDRESS, ROUTER_ABI, wallet);
    const veSuma = new ethers.Contract(VE_SUMA_ADDRESS, VESUMA_ABI, wallet);
    const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, wallet);
    const voting = new ethers.Contract(VOTING_ADDRESS, VOTING_ABI, wallet);
    
    // Check balances
    const [sumaBalance, wethBalance] = await Promise.all([
      sumaToken.balanceOf(address),
      wethToken.balanceOf(address)
    ]);
    
    console.log(`SUMA Balance: ${ethers.utils.formatEther(sumaBalance)}`);
    console.log(`WETH Balance: ${ethers.utils.formatEther(wethBalance)}`);
    
    // 1. Trading: SUMA -> WETH
    console.log("\n=== TRADING ===");
    const swapAmount = ethers.utils.parseEther("0.01");
    
    if (sumaBalance.gte(swapAmount)) {
      // Approve and execute swap
      await (await sumaToken.approve(ROUTER_ADDRESS, swapAmount)).wait();
      
      const path = [SUMA_TOKEN_ADDRESS, WETH_TOKEN_ADDRESS];
      const amounts = await router.getAmountsOut(swapAmount, path);
      const minOut = amounts[1].mul(99).div(100); // 1% slippage
      const deadline = Math.floor(Date.now() / 1000) + 300;
      
      const tx = await router.swapExactTokensForTokens(
        swapAmount,
        minOut,
        path,
        address,
        deadline
      );
      await tx.wait();
      console.log(`Swap successful: ${tx.hash}`);
    } else {
      console.log("Skipping trade: Insufficient SUMA");
    }
    
    // 2. Add Liquidity
    console.log("\n=== ADD LIQUIDITY ===");
    const sumaLiquidity = ethers.utils.parseEther("0.05");
    const wethLiquidity = ethers.utils.parseEther("0.005");
    
    if (sumaBalance.gte(sumaLiquidity) {
      // Approve tokens
      await (await sumaToken.approve(ROUTER_ADDRESS, sumaLiquidity)).wait();
      await (await wethToken.approve(ROUTER_ADDRESS, wethLiquidity)).wait();
      
      // Add liquidity
      const deadline = Math.floor(Date.now() / 1000) + 300;
      const tx = await router.addLiquidity(
        SUMA_TOKEN_ADDRESS,
        WETH_TOKEN_ADDRESS,
        sumaLiquidity,
        wethLiquidity,
        sumaLiquidity.mul(99).div(100),
        wethLiquidity.mul(99).div(100),
        address,
        deadline
      );
      await tx.wait();
      console.log(`Liquidity added: ${tx.hash}`);
    } else {
      console.log("Skipping liquidity: Insufficient tokens");
    }
    
    // 3. Convert SUMA to veSUMA
    console.log("\n=== CONVERT TO VESUMA ===");
    const convertAmount = ethers.utils.parseEther("0.03");
    
    if (sumaBalance.gte(convertAmount)) {
      await (await sumaToken.approve(VE_SUMA_ADDRESS, convertAmount)).wait();
      const tx = await veSuma.convertSuma(convertAmount);
      await tx.wait();
      console.log(`Conversion successful: ${tx.hash}`);
      
      const veBalance = await veSuma.balanceOf(address);
      console.log(`veSUMA Balance: ${ethers.utils.formatEther(veBalance)}`);
    } else {
      console.log("Skipping conversion: Insufficient SUMA");
    }
    
    // 4. Stake veSUMA
    console.log("\n=== STAKING ===");
    const veBalance = await veSuma.balanceOf(address);
    
    if (veBalance.gt(0)) {
      const stakeAmount = veBalance.div(2);
      await (await veSuma.approve(STAKING_ADDRESS, stakeAmount)).wait();
      
      const tx = await staking.stake(stakeAmount);
      await tx.wait();
      console.log(`Staked ${ethers.utils.formatEther(stakeAmount)} veSUMA: ${tx.hash}`);
      
      const earned = await staking.earned(address);
      console.log(`Current rewards: ${ethers.utils.formatEther(earned)}`);
    } else {
      console.log("Skipping staking: No veSUMA available");
    }
    
    // 5. Governance Voting
    console.log("\n=== GOVERNANCE ===");
    try {
      const proposals = await voting.getProposals();
      
      if (proposals.length > 0) {
        const proposalId = proposals[0];
        const hasVoted = await voting.hasVoted(proposalId, address);
        
        if (!hasVoted) {
          const tx = await voting.vote(proposalId, 1); // Vote "For"
          await tx.wait();
          console.log(`Voted on proposal ${proposalId}: ${tx.hash}`);
        } else {
          console.log(`Already voted on proposal ${proposalId}`);
        }
      } else {
        console.log("No active proposals");
      }
    } catch (e) {
      console.log(`Governance error: ${e.message}`);
    }
    
    console.log("\n=== BOT EXECUTION COMPLETE ===");
    
  } catch (error) {
    console.error("Bot failed:", error);
    process.exit(1);
  }
}

// Execute with proper cleanup
main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error("Unhandled error:", error);
    process.exit(1);
  });
