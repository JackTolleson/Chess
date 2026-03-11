import chess
import chess.engine

# Create board
board = chess.Board()

# Connect to Stockfish
engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
#should add a way to choose different skill levels on startup / new round
engine.configure({
    "UCI_LimitStrength":True,
    "UCI_Elo": 1350
})

while not board.is_game_over():
    print(board)
    print("\nYour move (e.g. chess e2e4): ")

    user_move = input().strip()
    #player concedes
    if user_move in ["resign", "quit", "exit"]:
        print("You resigned. Stockfish wins.")
        break    
    #player move
    try:
        move = chess.Move.from_uci(user_move)
        if move in board.legal_moves:
            board.push(move)
        else:
            print("Illegal move!\n")
            continue
    except:
        print("Invalid format!\n")
        continue

    # Engine move
    result = engine.play(board, chess.engine.Limit(time=0.1))
    print("Engine plays:", result.move)
    board.push(result.move)

print("Game over!")
engine.quit()
