liquidity = {
    ("tokenA", "tokenB"): (17, 10),
    ("tokenA", "tokenC"): (11, 7),
    ("tokenA", "tokenD"): (15, 9),
    ("tokenA", "tokenE"): (21, 5),
    ("tokenB", "tokenC"): (36, 4),
    ("tokenB", "tokenD"): (13, 6),
    ("tokenB", "tokenE"): (25, 3),
    ("tokenC", "tokenD"): (30, 12),
    ("tokenC", "tokenE"): (10, 8),
    ("tokenD", "tokenE"): (60, 25),
}
graph = {}

for key, value in liquidity.items():
    token_a, token_b = key
    reserve_in, reserve_out = value
    if token_a not in graph:
        graph[token_a] = []
    if token_b not in graph:
        graph[token_b] = []
    graph[token_a].append([token_b, reserve_in, reserve_out])
    graph[token_b].append([token_a, reserve_out, reserve_in])


def get_amount_out(amount_in, reserve_in, reserve_out):
    amount_in_with_fee = amount_in * 997
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in * 1000 + amount_in_with_fee
    amount_out = numerator / denominator
    return amount_out


def find_paths(start, end, graph, balance, path=None):
    paths = []

    if path is None:
        path = [start]
    else:
        path = path + [start]

    if start == end and len(path) > 1:
        return [(path, balance)]

    for next_token, reserve_in, reserve_out in graph[start]:
        if next_token not in path or (next_token == end and len(path) > 1):
            new_balance = get_amount_out(balance, reserve_in, reserve_out)
            paths.extend(find_paths(next_token, end, graph, new_balance, path))
    return paths


if __name__ == '__main__':
    arbitrage_paths = []

    for path, amount in find_paths("tokenB", "tokenB", graph, balance=5):
        if amount > 5:
            arbitrage_paths.append((path, amount))

    sorted_arbitrage_paths = sorted(arbitrage_paths, key=lambda x: x[1], reverse=True)

    if not sorted_arbitrage_paths:
        print("No profitable path found.")
    else:
        print('All paths:')
        for path, balance in sorted_arbitrage_paths:
            formatted_path = "->".join(path)
            print(f'path: {formatted_path}, tokenB balance={balance:.18f}.')

        print('\nThe most profitable path:')
        print(f'path: {"->".join(sorted_arbitrage_paths[0][0])}, tokenB balance={sorted_arbitrage_paths[0][1]:.18f}.')
