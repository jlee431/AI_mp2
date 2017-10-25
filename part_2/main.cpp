#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <utility>
#include <vector>

#define BOARD_WIDTH 8

using namespace std;

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

    State(const State &other) : state(other.state) {
        for (int i = 0; i < 2; ++i) piecesLeft[i] = other.piecesLeft[i];
    }

    State& operator=(const State &other) {
        if (this != &other) {
            state = other.state;
            for (int i = 0; i < 2; ++i) piecesLeft[i] = other.piecesLeft[i];
        }
        return *this;
    }

    Worker checkWinner() {
        for (int i = 0; i < 2; ++i) {
            if (!piecesLeft[(~i) & 1]) return static_cast<Worker>(i);
        }
        for (int i = 0; i < WIDTH; ++i) {
            if (state[WIDTH - 1][i] == Worker::BLACK) return Worker::BLACK;
            if (state[0][i] == Worker::WHITE) return Worker::WHITE;
        };
        return Worker::NONE;
    }

    bool isLegalMove(Move &move) {
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

    vector<Move> possibleMoves(Worker worker) {

        Position next[2][3] = {
            {{-1, 1}, {0, 1}, {1, 1}},
            {{-1, -1}, {0, -1}, {1, -1}}
        };

        int posSel = static_cast<int>(worker);

        Move tempMove;

        vector<Move> output;

        for (int y = 0; y < WIDTH; ++y) {
            for (int x = 0; x < WIDTH; ++x) {
                for (int i = 0; i < 3; ++i) {
                    tempMove = make_pair<Position, Position>(Position(x, y), Position(x, y) + next[posSel][i]);
                    if (isLegalMove(tempMove)) output.push_back(tempMove);
                } // end i
            } // end x
        } // end y

        return output;

    } // end possibleMoves

    // TODO
    // State move(Move &move) {}

    Worker opponent(Worker worker) {
        return static_cast<Worker>((~static_cast<int>(worker)) & 1);
    }

    int getPiecesLeft(Worker worker) {
        return piecesLeft[static_cast<int>(worker)];
    }

    const vector<vector<Worker>>& getState() {
        return state;
    }

}; // end class State

template<typename H>
class Player {

    Worker worker;
    const H heuristic_f;

    int numOfExpandedNodes;

    // TODO
    // vector<int> expandedNodesVec;
    // vector<time> timeVec;

    int capturedWorkers;

    bool useAlphaBeta;
    int depth;

public:

    Player(Worker w, const H &h, bool useAlphaBeta = false)
      : worker(w)
      , heuristic_f(h)
      , numOfExpandedNodes(0)
      , capturedWorkers(0)
      , useAlphaBeta(useAlphaBeta)
      , depth(useAlphaBeta ? 5 : 3)
    { }

    // TODO
    /* Move nextMove(State state, int curentDepth) {

    }

    Move nextMove(State &state) {
        return nextMove(state, depth);
    } */

};

double myRand() {
    srand(time(0));
    return (rand() % 100) / 100.0;
}

int main() {

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

    State state;

    // delete later
    defHeuristic_1(state, Worker::BLACK);
    offHeuristic_1(state, Worker::BLACK);
    defHeuristic_2(state, Worker::BLACK);
    offHeuristic_2(state, Worker::BLACK);

    return 0;

}
