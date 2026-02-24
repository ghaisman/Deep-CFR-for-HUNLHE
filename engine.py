import numpy as np
import time
from phevaluator.evaluator import evaluate_cards
import random

SB = 1
BB = 2
START_STACK = 400


PREFLOP = 0
FLOP = 1
TURN = 2
RIVER = 3
SHOWDOWN = 4

FOLD = -2
CHECK = -1
CALL = 0
RAISE05 = 0.5
RAISE1 = 1.0
RAISE15 = 1.5
RAISE2 = 2.0
RAISE25 = 2.5
ALLIN = 3.0


def init_state_vector():
    """
    Returns initialized state vector with dealt cards etc
    """
    cards = np.arange(52)
    np.random.shuffle(cards)
    button = 0
    street = 0
    state_vector = (button, street, SB, BB, cards)
    return state_vector


actions = [FOLD, CALL, CHECK, RAISE05, RAISE1, RAISE15, RAISE2, RAISE25, ALLIN]


def compute_raise_pips(oldbutton, oldpip0, oldpip1, action):
    """
    Calculates new pips after a raise.
    Raiser first calls, then raises by action * pot_after_call.
    """
    if oldbutton == 0:
        my_pip, opp_pip = oldpip0, oldpip1
    else:
        my_pip, opp_pip = oldpip1, oldpip0

    pot_after_call = 2 * opp_pip
    raise_amount = action * pot_after_call
    new_my_pip = opp_pip + raise_amount  # call + raise on top
    new_my_pip = min(new_my_pip, START_STACK)

    if oldbutton == 0:
        return new_my_pip, oldpip1
    else:
        return oldpip0, new_my_pip


def proceed(state, action):
    """
    Takes current state and action, returns new state or reward if hand ended.
    """
    oldbutton = state[0]
    oldstreet = state[1]
    oldpip0 = state[2]
    oldpip1 = state[3]
    cards = state[4]

    if oldstreet == PREFLOP:  # preflop
        if action == FOLD:
            return -oldpip0 if oldbutton == 0 else oldpip1
        elif action == CALL:
            if oldbutton == 0:
                if oldpip1 == BB:
                    next_state = (1, PREFLOP, BB, BB, cards)
                else:
                    next_state = (1, FLOP, oldpip1, oldpip1, cards)
            else:
                next_state = (1, FLOP, oldpip0, oldpip0, cards)
            if next_state[2] == START_STACK:
                return (1, SHOWDOWN, START_STACK, START_STACK, cards)
        elif action == CHECK:
            next_state = (1, FLOP, BB, BB, cards)
        elif action >= RAISE05 and action < ALLIN:
            pip_0, pip_1 = compute_raise_pips(oldbutton, oldpip0, oldpip1, action)
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)
        elif action == ALLIN:
            if oldbutton == 0:
                pip_0 = START_STACK
                pip_1 = oldpip1
            else:
                pip_0 = oldpip0
                pip_1 = START_STACK
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)

    elif oldstreet == FLOP:  # postflop
        if action == FOLD:
            return -oldpip0 if oldbutton == 0 else oldpip1
        elif action == CALL:
            if oldbutton == 0:
                next_state = (1, TURN, oldpip1, oldpip1, cards)
            else:
                next_state = (1, TURN, oldpip0, oldpip0, cards)
            if next_state[2] == START_STACK:
                return (1, SHOWDOWN, START_STACK, START_STACK, cards)
        elif action == CHECK:
            if oldbutton == 0:  # proceed to turn
                next_state = (1, TURN, oldpip0, oldpip1, cards)
            else:  # stay on same street
                next_state = (0, oldstreet, oldpip0, oldpip1, cards)
        elif action >= RAISE05 and action < ALLIN:
            pip_0, pip_1 = compute_raise_pips(oldbutton, oldpip0, oldpip1, action)
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)
        elif action == ALLIN:
            if oldbutton == 0:
                pip_0 = START_STACK
                pip_1 = oldpip1
            else:
                pip_0 = oldpip0
                pip_1 = START_STACK
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)

    elif oldstreet == TURN:  # postturn
        if action == FOLD:
            return -oldpip0 if oldbutton == 0 else oldpip1
        elif action == CALL:
            if oldbutton == 0:
                next_state = (1, RIVER, oldpip1, oldpip1, cards)
            else:
                next_state = (1, RIVER, oldpip0, oldpip0, cards)
            if next_state[2] == START_STACK:
                return (1, SHOWDOWN, START_STACK, START_STACK, cards)
        elif action == CHECK:
            if oldbutton == 0:  # proceed to river
                next_state = (1, RIVER, oldpip0, oldpip1, cards)
            else:  # stay on same street
                next_state = (0, oldstreet, oldpip0, oldpip1, cards)
        elif action >= RAISE05 and action < ALLIN:
            pip_0, pip_1 = compute_raise_pips(oldbutton, oldpip0, oldpip1, action)
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)
        elif action == ALLIN:
            if oldbutton == 0:
                pip_0 = START_STACK
                pip_1 = oldpip1
            else:
                pip_0 = oldpip0
                pip_1 = START_STACK
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)

    elif oldstreet == RIVER:  # postriver
        if action == FOLD:
            return -oldpip0 if oldbutton == 0 else oldpip1
        elif action == CALL:
            if oldbutton == 0:
                next_state = (1, SHOWDOWN, oldpip1, oldpip1, cards)
            else:
                next_state = (1, SHOWDOWN, oldpip0, oldpip0, cards)
        elif action == CHECK:
            if oldbutton == 0:  # second to act checks → showdown
                next_state = (1, SHOWDOWN, oldpip0, oldpip1, cards)
            else:  # first to act checks → opponent acts
                next_state = (0, oldstreet, oldpip0, oldpip1, cards)
        elif action >= RAISE05 and action < ALLIN:
            pip_0, pip_1 = compute_raise_pips(oldbutton, oldpip0, oldpip1, action)
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)
        elif action == ALLIN:
            if oldbutton == 0:
                pip_0 = START_STACK
                pip_1 = oldpip1
            else:
                pip_0 = oldpip0
                pip_1 = START_STACK
            next_state = ((1 - oldbutton), oldstreet, pip_0, pip_1, cards)
    elif oldstreet == SHOWDOWN:  # showdown
        # evaluate hands and return reward
        assert oldpip0 == oldpip1
        hand0 = cards[:2].astype(object)
        hand1 = cards[2:4].astype(object)
        board = cards[4:9].astype(object)
        # evaluate hand strength and determine winner
        hand0_strength = evaluate_cards(*hand0, *board)
        hand1_strength = evaluate_cards(*hand1, *board)
        if hand0_strength < hand1_strength:
            return oldpip1
        elif hand1_strength > hand0_strength:
            return -oldpip0
        else:
            return 0
    return next_state


def get_legal_actions(state):
    button, street, pip0, pip1, cards = state
    to_call = max(pip0, pip1) - min(pip0, pip1)

    if to_call == 0:
        legal = [CHECK]
    else:
        legal = [FOLD, CALL]

    # Only add raises that produce distinct pip values below all-in
    seen_allin = False
    for r in [RAISE05, RAISE1, RAISE15, RAISE2, RAISE25]:
        p0, p1 = compute_raise_pips(button, pip0, pip1, r)
        new_pip = p0 if button == 0 else p1
        if new_pip >= START_STACK:
            seen_allin = True
            break
        legal.append(r)

    legal.append(ALLIN)
    return legal



def test_speed():
    ########TEST SPEED OF 1M INIT and FOLDS#######
    start_time = time.time()

    for i in range(1_000_000):
        start = init_state_vector()
        proceeded = proceed(start, FOLD)

    end_time = time.time()

    print("Steps/s: ", 1_000_000 / (end_time - start_time))

    #######SIMULATE 1M hands with random actions#######

    start_time = time.time()
    for i in range(1_000_000):
        s = init_state_vector()
        done = False
        while not done:
            legal_actions = get_legal_actions(s)
            action = random.choice(legal_actions)
            result = proceed(s, action)
            if isinstance(result, tuple):
                s = result
            else:
                done = True
    end_time = time.time()
    print("Hands/s: ", 1_000_000 / (end_time - start_time))

if __name__ == "__main__":
    #test_speed()
    pass
