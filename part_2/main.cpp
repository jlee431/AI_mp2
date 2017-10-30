#include <algorithm>
#include <chrono>
#include <climits>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <string>
#include <utility>
#include <vector>

#define BOARD_WIDTH 8

using namespace std;

class Timer {
    // credit: https://gist.github.com/tzutalin/fd0340a93bb8d998abb9
    typedef std::chrono::high_resolution_clock clock_;
    std::chrono::time_point<clock_> m_beg;
public:
    Timer() : m_beg(clock_::now()) {}
    void reset() { m_beg = clock_::now(); }
    double elapsed() const {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            clock_::now() - m_beg
        ).count();
    }
};

struct Position {
    int x, y;
    Position() : x(-1), y(-1) {}
    Position(int x, int y) : x(x), y(y) {}
    Position operator+(const Position &p) {
        return Position(x + p.x, y + p.y);
    }
};

typedef pair<Position, Position> Move;

enum class Worker : int { BLACK, WHITE, NONE };

class State {

    const int WIDTH = BOARD_WIDTH;

    vector<vector<Worker>> state;

    // 0: black; 1: white
    int piecesLeft[2];

public:

    State() {
        state.assign(WIDTH, vector<Worker>(WIDTH, Worker::NONE));
        for (int i = 0; i < 2; ++i) {
            piecesLeft[i] = WIDTH * 2;
            for (int j = 0; j < WIDTH; ++j) {
                state[i][j] = Worker::BLACK;
                state[WIDTH - i - 1][j] = Worker::WHITE;
            }
        }
    }

    State(const State &other) {
        state.assign(WIDTH, vector<Worker>(WIDTH, Worker::NONE));
        for (int y = 0; y < WIDTH; ++y) {
            for (int x = 0; x < WIDTH; ++x) {
                state[y][x] = other.state[y][x];
            }
        }
        for (int i = 0; i < 2; ++i) piecesLeft[i] = other.piecesLeft[i];
    }

    State& operator=(const State &other) {
        if (this != &other) {
            state.assign(WIDTH, vector<Worker>(WIDTH, Worker::NONE));
            for (int y = 0; y < WIDTH; ++y) {
                for (int x = 0; x < WIDTH; ++x) {
                    state[y][x] = other.state[y][x];
                }
            }
            for (int i = 0; i < 2; ++i) piecesLeft[i] = other.piecesLeft[i];
        }
        return *this;
    }

    // assuming legal move
    State nextState(const Move move) {
        State newState = *this;
        int dieWorker = static_cast<int>(newState.state[move.second.y][move.second.x]);
        if (dieWorker < 2) --newState.piecesLeft[dieWorker];
        newState.state[move.second.y][move.second.x] = newState.state[move.first.y][move.first.x];
        newState.state[move.first.y][move.first.x] = Worker::NONE;
        return newState;
    }

    Worker checkWinner() const {
        for (int i = 0; i < 2; ++i) {
            if (!piecesLeft[(~i) & 1]) return static_cast<Worker>(i);
        }
        for (int i = 0; i < WIDTH; ++i) {
            if (state[WIDTH - 1][i] == Worker::BLACK) return Worker::BLACK;
            if (state[0][i] == Worker::WHITE) return Worker::WHITE;
        };
        return Worker::NONE;
    }

    bool isLegalMove(const Move &move) const {
        // first --> second
        if (
            move.second.x < 0 ||
            move.second.x >= WIDTH ||
            move.second.y < 0 ||
            move.second.y >= WIDTH ||
            state[move.first.y][move.first.x] == state[move.second.y][move.second.x] ||
            (state[move.second.y][move.second.x] != Worker::NONE && move.first.y == move.second.y)
        ) {
            return false;
        }
        return true;
    }

    vector<Move> possibleMoves(const Worker worker) const {

        Position next[2][3] = {
            {{-1, 1}, {0, 1}, {1, 1}},
            {{-1, -1}, {0, -1}, {1, -1}}
        };

        int posSel = static_cast<int>(worker);

        Move tempMove;

        vector<Move> output;

        for (int y = 0; y < WIDTH; ++y) {
            for (int x = 0; x < WIDTH; ++x) {
                if (state[y][x] != worker) continue;
                for (int i = 0; i < 3; ++i) {
                    tempMove = make_pair<Position, Position>(Position(x, y), Position(x, y) + next[posSel][i]);
                    if (isLegalMove(tempMove)) output.push_back(tempMove);
                } // end i
            } // end x
        } // end y

        return output;

    } // end possibleMoves

    Worker opponent(const Worker worker) const {
        return static_cast<Worker>((~static_cast<int>(worker)) & 1);
    }

    int getPiecesLeft(const Worker worker) const {
        return piecesLeft[static_cast<int>(worker)];
    }

    const vector<vector<Worker>>& getState() const {
        return state;
    }

    string toString() {
        string output = "  0 1 2 3 4 5 6 7\n";
        char temp;
        for (int y = 0; y < BOARD_WIDTH; ++y) {
            output.push_back(y + '0');
            output.push_back(' ');
            for (int x = 0; x < BOARD_WIDTH; ++x) {
                switch (state[y][x]) {
                    case Worker::WHITE: temp = 'W'; break;
                    case Worker::BLACK: temp = 'B'; break;
                    default: temp = ' '; break;
                }
                output.push_back(temp);
                output.push_back(' ');
            }
            output.push_back('\n');
        }
        output += "-------------------";
        return output;
    }

}; // end class State

class DummyPlayer {
protected:
    vector<int> expandedNodesVec;
    vector<double> timeVec; // milliseconds
public:
    virtual ~DummyPlayer() {}
    virtual Move nextMove(State&) = 0;
    const vector<int>& getExpandedNodesVec() {
        return expandedNodesVec;
    }

    const vector<double>& getTimeVec() {
        return timeVec;
    }
};

template<typename H>
class Player : public DummyPlayer {

    const Worker worker;
    const H &heuristic_f;

    int numOfExpandedNodes;

    int capturedWorkers;

    const bool useAlphaBeta;
    const int depth;

    Timer timer;

public:

    Player(const Worker w, const H &h, bool useAlphaBeta = false)
      : worker(w)
      , heuristic_f(h)
      , numOfExpandedNodes(0)
      , capturedWorkers(0)
      , useAlphaBeta(useAlphaBeta)
      , depth(useAlphaBeta ? 3 : 3)
    { }

    ~Player() override {}

    double minMax(
        State state,
        const int curentDepth,
        const Worker currentWorker,
        double &alphaScore,
        double &betaScore,
        int &expandedNodes
    ) {

        if (curentDepth == 0) return heuristic_f(state, currentWorker);

        const bool isMax = currentWorker == worker;

        vector<Move> moves = state.possibleMoves(currentWorker);
        const int N = moves.size();

        double bestScore = isMax ? INT_MIN : INT_MAX, tempScore;

        auto comp = [&isMax](double tempScore, double bestScore) -> bool {
            if (isMax) return tempScore > bestScore;
            return tempScore < bestScore;
        };

        for (int i = 0; i < N; ++i) {

            tempScore = minMax(
                state.nextState(moves[i]),
                curentDepth - 1,
                state.opponent(currentWorker),
                alphaScore,
                betaScore,
                ++expandedNodes
            );

            if (comp(tempScore, bestScore)) bestScore = tempScore;

            if (useAlphaBeta) {
                if (isMax) {
                    if (bestScore > betaScore) break;
                    if (bestScore > alphaScore) alphaScore = bestScore;
                } else {
                    if (bestScore < alphaScore) break;
                    if (bestScore < betaScore) betaScore = bestScore;
                }
            }

        } // end for i

        return bestScore;

    } // end alphaBeta

    Move nextMove(State &state) override {

        double alphaScore = INT_MIN, betaScore = INT_MAX;

        vector<Move> moves = state.possibleMoves(worker);
        const int N = moves.size();

        double bestScore = INT_MIN, tempScore;
        int best_i = 0;

        int expandedNodes = 0;

        timer.reset();

        for (int i = 0; i < N; ++i) {
            tempScore = minMax(
                state.nextState(moves[i]),
                depth - 1,
                state.opponent(worker),
                alphaScore,
                betaScore,
                ++expandedNodes
            );
            if (tempScore > bestScore) {
                bestScore = tempScore;
                best_i = i;
            }
        }

        timeVec.push_back(timer.elapsed());

        expandedNodesVec.push_back(expandedNodes);

        return moves[best_i];

    } // end nextMove

}; // end class Player

double myRand() {
    srand(time(0));
    return (rand() % 100) / 100.0;
}

int test(int player0, int player1, int useAlphaBeta) {

    auto defHeuristic_1 = [](State &state, Worker worker) -> double {
        // 2 * number_of_own_pieces_remaining + random()
        return 2 * state.getPiecesLeft(worker) + myRand();
    };

    auto offHeuristic_1 = [](State &state, Worker worker) -> double {
        // 2 * (30 - number_of_opponent_pieces_remaining) + random()
        return 2 * (30 - state.getPiecesLeft(state.opponent(worker))) + myRand();
    };

    auto defHeuristic_2 = [](State &state, Worker worker) -> double {
        // 2 * (num of own peices on side of board) - (num of opponents pieces across middle) + random()

        const vector<vector<Worker>>& board = state.getState();

        Worker opponent = state.opponent(worker);

        int ownPiecesOnTheBorder = 0, opponentsPiecesAcrossMiddle = 0;
        int yOffset = (BOARD_WIDTH >> 1) - ((static_cast<int>(worker) * BOARD_WIDTH) >> 1);

        for (int y = 0; y < BOARD_WIDTH; ++y) {
            if (board[y][0] == worker) ++ownPiecesOnTheBorder;
            if (board[y][BOARD_WIDTH - 1] == worker) ++ownPiecesOnTheBorder;
        }

        for (int y = 0 + yOffset; y < yOffset + (BOARD_WIDTH >> 1); ++y) {
            for (int x = 0; x < BOARD_WIDTH; ++x) {
                if (board[y][x] == opponent) ++opponentsPiecesAcrossMiddle;
            }
        }

        return 2 * ownPiecesOnTheBorder - opponentsPiecesAcrossMiddle + myRand();

    }; // end defHeuristic_2

    auto offHeuristic_2 = [](State &state, Worker worker) -> double {
        // 2 * (Distance of farthest own piece) + random()

        const vector<vector<Worker>>& board = state.getState();

        int farthestOwnPiece = -1, startY = BOARD_WIDTH - 1, endY = 0, nextY = -1;
        bool foundFarthest = false;

        if (worker == Worker::WHITE) {
            swap(startY, endY);
            nextY *= -1;
        }

        for (int y = startY; !foundFarthest && y - nextY != endY; y += nextY) {
            for (int x = 0; !foundFarthest && x < BOARD_WIDTH; ++x) {
                if (board[y][x] == worker) {
                    foundFarthest = true;
                    farthestOwnPiece = y;
                }
            }
        }

        return 2 * farthestOwnPiece + myRand();

    }; // end offHeuristic_2

    int playerH[2] = {player0, player1};

    State state;

    DummyPlayer **player = new DummyPlayer*[2];

    Move nextMove;
    // int currentPlayer = (myRand() < 0.5) ? 0 : 1;
    int currentPlayer = 0;

    for (int i = 0; i < 2; ++i) {
        switch (playerH[i]) {
            case 1:
                player[i] = new Player<decltype(defHeuristic_1)>(static_cast<Worker>(i), defHeuristic_1, useAlphaBeta);
                break;
            case 2:
                player[i] = new Player<decltype(offHeuristic_1)>(static_cast<Worker>(i), offHeuristic_1, useAlphaBeta);
                break;
            case 3:
                player[i] = new Player<decltype(defHeuristic_2)>(static_cast<Worker>(i), defHeuristic_2, useAlphaBeta);
                break;
            case 4:
                player[i] = new Player<decltype(offHeuristic_2)>(static_cast<Worker>(i), offHeuristic_2, useAlphaBeta);
                break;
        }
    }

    int totalMoves = 0;

    while (state.checkWinner() == Worker::NONE) {
        ++totalMoves;
        currentPlayer = static_cast<int>(state.opponent(static_cast<Worker>(currentPlayer)));
        nextMove = player[currentPlayer]->nextMove(state);
        system("cls");
        printf(
            "%c: (%d, %d) --> (%d, %d)\n",
            static_cast<Worker>(currentPlayer) == Worker::WHITE ? 'W' : 'B',
            nextMove.first.x,
            nextMove.first.y,
            nextMove.second.x,
            nextMove.second.y
        );
        state = state.nextState(nextMove);
        string str = state.toString();
        puts(str.c_str());
    }

    printf("winner: player%d\n", currentPlayer + 1);
    printf("totalMoves = %d\n", totalMoves);

    puts("\nexpandedNodes:\n");
    for (int i = 0; i < 2; ++i) {
        printf("player%d:\n", i);
        int totalNodes = 0;
        double totalTime = 0;

        const vector<int> &expandedNodesVec = player[i]->getExpandedNodesVec();
        const vector<double> &timeVec = player[i]->getTimeVec();

        for (int nodes : expandedNodesVec) totalNodes += nodes;
        for (double time : timeVec) totalTime += time;

        printf("totalNodes = %d\n", totalNodes);
        printf("average Nodes = %f\n", (double) totalNodes / expandedNodesVec.size());
        printf("totalTime = %f\n", totalTime);
        printf("average time = %f\n", totalTime / timeVec.size());
        putchar('\n');
    }

    for (int i = 0; i < 2; ++i) delete player[i];
    delete[] player;

    return currentPlayer;

}

int main() {

    int useAlphaBeta = 0;
    int winGames[2] = {0, 0};
    // int player0 = 1, player1 = 4;
    int player0 = 2, player1 = 3;

    // scanf("%d", &useAlphaBeta);
    /* for (int i = 0; i < 2; ++i) {
        do {
            printf("player%d: ", i + 1);
            scanf("%d", &playerH[i]);
        } while(playerH[i] <= 0 || playerH[i] >= 5); // change to < 0 for human player
    } */

    for (int i = 0; i < 1; ++i) {
        printf("i = %d\n", i);
        ++winGames[test(player0, player1, useAlphaBeta)];
    }

    printf("%d:%d\n", winGames[0], winGames[1]);

    return 0;

}
