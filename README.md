# 2024-Spring-HW2

Please complete the report problem below:

## Problem 1
Provide your profitable path, the amountIn, amountOut value for each swap, and your final reward (your tokenB balance).

> Solution

#### path: tokenB->tokenA->tokenD->tokenC->tokenB  
Swap tokenB to tokenA: amountIn=5, amountOut=5.655321988655322  
Swap tokenA to tokenD: amountIn=5.655321988655322, amountOut=2.4587813170979333  
Swap tokenD to tokenC: amountIn=2.4587813170979333, amountOut=5.0889272933015155  
Swap tokenC to tokenB: amountIn=5.0889272933015155, amountOut=20.129888944077443  
#### Final reward (tokenB balance): 20.129888944077443  


## Problem 2
What is slippage in AMM, and how does Uniswap V2 address this issue? Please illustrate with a function as an example.

> Solution

### What is slippage in AMM?
在 AMM 中，代幣的價格是根據流動池內的代幣數量以某種公式（例如 x * y = k）計算得到的，當 x 增加時，為了保持 k 的不變，y 必須相應的減少，表示 x 換成 y 的成本也在增加，因此當發生大額交易或是交易對的流動性不夠時，在交易中實際獲得的代幣數量與在沒有滑點的理想情況下應該獲得的代幣數量之間有落差，這個落差就是滑點(slippage)。  

#### Example
```python
print(f'liquidity:(100,500), amount in = 1, amount out = {get_amount_out(1, 100, 500)} 
    => token A : token B = 1 : {get_amount_out(1, 100, 500)/1}')
print(f'liquidity:(100,500), amount in = 50, amount out = {get_amount_out(50, 100, 500)} 
    => token A : token B = 1 : {get_amount_out(50, 100, 500)/50}')
print(f'liquidity:(100,500), amount in = 100, amount out = {get_amount_out(100, 100, 500)} 
    => token A : token B = 1 : {get_amount_out(100, 100, 500)/100}')
print(f'liquidity:(1000,5000), amount in = 100, amount out = {get_amount_out(100, 1000, 5000)} 
    => token A : token B = 1 : {get_amount_out(100, 1000, 5000)/100}')
```

```
liquidity:(100,500), amount in = 1, amount out = 4.935790171985307 => token A : token B = 1 : 4.935790171985307  
liquidity:(100,500), amount in = 50, amount out = 166.332999666333 => token A : token B = 1 : 3.32665999332666  
liquidity:(100,500), amount in = 100, amount out = 249.62443665498247 => token A : token B = 1 : 2.4962443665498246  
liquidity:(1000,5000), amount in = 100, amount out = 453.30544694007455 => token A : token B = 1 : 4.533054469400746  
```

### How does Uniswap V2 address this issue?
`swapExactTokensForTokens`, `swapExactETHForTokens` and `swapExactTokensForETH` function has slippage check: 
```solidity
require(amounts[amounts.length - 1] >= amountOutMin, 'UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT');
```

首先根據用戶設定的 slippage tolerance 計算出 amountOutMin，並且在 swap token 時進行檢查，當最後獲得的 token amount 小於 amountOutMin 時，revert 這筆交易。  
#### Example:  
假設 Alice 想要將 1 個 token A 換成 100 個 token B，Alice 將 slippage tolerance 設定為 5 %，計算出 amountOutMin 為 95 個 token B，表示即使市場價格發生變動， Alice 預期在交易完成後至少能夠換得 95 個 token B。


## Problem 3
Please examine the mint function in the UniswapV2Pair contract. Upon initial liquidity minting, a minimum liquidity is subtracted. What is the rationale behind this design?

> Solution

```solidity
uint public constant MINIMUM_LIQUIDITY = 10**3;
if (_totalSupply == 0) {
    liquidity = Math.sqrt(amount0.mul(amount1)).sub(MINIMUM_LIQUIDITY);
    _mint(address(0), MINIMUM_LIQUIDITY); // permanently lock the first MINIMUM_LIQUIDITY tokens
}
```
在首次提供流動性時，需要扣除 1000 個 LP token，目的是為了防止 inflation attack，在一個新的流動池中，攻擊者作為第一個流動性提供者，以很少的代幣佔了所有的份額，之後再透過 transfer 或其他某種方式只增加了流動性池中的資產而沒有相應增加 LP token 總供應量，使得原本的 LP token 有了更多的價值，進一步犧牲了後來加入的流動性提供者的權益，在首次提供流動性時燒毀 MINIMUM_LIQUIDITY 數量的 LP token，確保透過這種方式操縱 LP token 的價值時需要付出很大的成本，同時防止某個人控制了整個流動性池。


## Problem 4
Investigate the minting function in the UniswapV2Pair contract. When depositing tokens (not for the first time), liquidity can only be obtained using a specific formula. What is the intention behind this?

> Solution

```solidity
liquidity = Math.min(amount0.mul(_totalSupply) / _reserve0, amount1.mul(_totalSupply) / _reserve1);
```
用戶在提供流動性時，獲得的 LP token 數量為存入的代幣佔整個流動池的比例與目前 LP 總供應量的乘積，取兩種比例的最小值的原因是為了激勵流動性提供者按照流動性池當前代幣比例增加資金，以避免獲得較少的 LP token，按照流動池現有比例增加流動性有助於維護代幣間的相對價值，避免因不平衡的供應而造成的價格波動。


## Problem 5
What is a sandwich attack, and how might it impact you when initiating a swap?

> Solution

當我們使用 AMM 進行代幣交換時，這筆交易在被打包上鏈前會在 mempool 中等待，攻擊者透過提高 gas fee 等方式調整交易被打包的順序，並在我們這筆交易的前後添加對他有利的交易，導致我們在做代幣的交換時有較大的 slippage。

#### Example:  
假設目前 ETH/DAI 的匯率為 1:3000，Alice 想要將 1 ETH 換成 3000 DAI

1. 攻擊者搶先在 Alice 之前提交一個用 ETH 買入 DAI 的交易，提高了 DAI 相對於 ETH 的價格
2. 由於 DAI 相對於 ETH 的價格被攻擊者提高了，Alice 能換到的 DAI 會少於 3000
3. 在 Alice 的交易後，攻擊者立即提交一個賣出 DAI 的交易，來獲得比一開始投入還要多的 ETH 

