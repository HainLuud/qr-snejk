import game

def generateTrainData(self):
    training_data = []
    # all scores:
    scores = []
    # just the scores that met our threshold:
    goodGameScores = []

    # For 1000 games
    for i in range(1000): 

        score = 100
        # moves specifically from this environment:
        gameMemory = []
        # previous board that we saw
        prevState = []

        # for 300 steps each game
        for j in range(300):
            snek = game.Snake(3, [(1,11), (1,12), (1,13), (1,14), (1,15)], "random")
            # choose random move
            move = random.choice(snek.randomMove())
            board, reward, gameOver = snek.move(move)

            gameMemory.append([prevState, move])
            prevState = board
            score += reward
            if gameOver: break

        if score >= 20:
            goodGameScores.append(score)
            for data in gameMemory:
                # convert move to one-hot (output for NN)
                UP, DOWN, LEFT, RIGHT = ((0,-1), (0,1), (-1,0), (1,0))
                moveToOneHot = {UP:[0, 0, 0, 1], DOWN:[0, 0, 1, 0], LEFT:[0, 1, 0, 0], RIGHT:[1, 0, 0, 0] }
                # saving our training data
                training_data.append([data[0], moveToOneHot[data[1]]])

        # save overall scores
        scores.append(score)

    # some stats here, to further illustrate the neural network magic!
    print('Average accepted score:', mean(goodGameScores))
    print('Score Requirement:', score_requirement)
    print('Median score for accepted scores:', median(goodGameScores))
    print(Counter(goodGameScores))
    score_requirement = mean(goodGameScores)

    # just in case you wanted to reference later
    #training_data_save = np.array([training_data, score_requirement])
    #np.save('saved.npy', training_data_save)

    return training_data


game.main()