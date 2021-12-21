import random
import numpy as np
import math
from random import choice
import statistics

startingSudoku = """
                    024007000
                    600000000
                    003680415
                    431005000
                    500000032
                    790000060
                    209710800
                    040093000
                    310004750
                """

sudoku = np.array([[int(i) for i in line] for line in startingSudoku.split()])


def printSudoku(sudoku):

    print("\n")

    for i in range(len(sudoku)):

        line = ""

        if i == 3 or i == 6:
            print("---------------------")

        for j in range(len(sudoku[i])):

            if j == 3 or j == 6:
                line += "| "

            line += str(sudoku[i, j]) + " "

        print(line)


def identifyFixedSudokuValues(startingSudoku):

    for i in range(0, 9):
        for j in range(0, 9):
            if startingSudoku[i, j] != 0:
                startingSudoku[i, j] = 1

    return (startingSudoku)


# Cost Function
def costFunction(sudoku):

    numberOfErrors = 0

    for i in range(0, 9):
        numberOfErrors += calculateErrorOnIthRowCol(i, i, sudoku)

    return (numberOfErrors)


def calculateErrorOnIthRowCol(row, column, sudoku):

    numberOfErrors = (9 - len(np.unique(sudoku[:, column]))) + (9 - len(np.unique(sudoku[row, :])))

    return (numberOfErrors)


def createList3x3Blocks():

    finalListOfBlocks = []

    for r in range(0, 9):

        tmpList = []

        block1 = [i + 3 * ((r) % 3) for i in range(0, 3)]
        block2 = [i + 3 * math.trunc((r) / 3) for i in range(0, 3)]

        for x in block1:
            for y in block2:
                tmpList.append([x, y])

        finalListOfBlocks.append(tmpList)

    return (finalListOfBlocks)


def fillNondeterministically3x3Blocks(sudoku, listOfBlocks):

    for block in listOfBlocks:
        for cell in block:

            if sudoku[cell[0], cell[1]] == 0:
                currentBlock = sudoku[block[0][0] : (block[-1][0] + 1), block[0][1] : (block[-1][1] + 1)]
                sudoku[cell[0], cell[1]] = choice([i for i in range(1, 10) if i not in currentBlock])

    return sudoku


def summationOfCellsOfOneBlock(sudoku, oneBlock):

    finalSum = 0

    for box in oneBlock:
        finalSum += sudoku[box[0], box[1]]

    return (finalSum)


def chooseTwoRandomBoxesWithinBlock(fixedSudoku, block):

    while (1):

        firstBox = random.choice(block)
        secondBox = choice([cell for cell in block if cell is not firstBox])

        if fixedSudoku[firstBox[0], firstBox[1]] != 1 and fixedSudoku[secondBox[0], secondBox[1]] != 1:
            return ([firstBox, secondBox])


def flipCells(sudoku, cellsToFlip):

    newSudokuCertificate = np.copy(sudoku)
    placeHolder = newSudokuCertificate[cellsToFlip[0][0], cellsToFlip[0][1]]
    newSudokuCertificate[cellsToFlip[0][0], cellsToFlip[0][1]] = newSudokuCertificate[cellsToFlip[1][0], cellsToFlip[1][1]]
    newSudokuCertificate[cellsToFlip[1][0], cellsToFlip[1][1]] = placeHolder
    return (newSudokuCertificate)


def generateNewSudokuCertificate(sudoku, fixedSudoku, listOfBlocks):

    randomBlock = random.choice(listOfBlocks)

    if summationOfCellsOfOneBlock(fixedSudoku, randomBlock) > 6:
        return (sudoku, 1, 1)

    cellsToFlip = chooseTwoRandomBoxesWithinBlock(fixedSudoku, randomBlock)
    newSudokuCertificate = flipCells(sudoku, cellsToFlip)

    return ([newSudokuCertificate, cellsToFlip])


def ChooseNewState(currentSudoku, fixedSudoku, listOfBlocks, sigma):

    proposal = generateNewSudokuCertificate(currentSudoku, fixedSudoku, listOfBlocks)
    newSudoku = proposal[0]
    boxesToCheck = proposal[1]

    currentCost = calculateErrorOnIthRowCol(boxesToCheck[0][0],
                                            boxesToCheck[0][1],
                                            currentSudoku) + calculateErrorOnIthRowCol(boxesToCheck[1][0],
                                                                                       boxesToCheck[1][1],
                                                                                       currentSudoku)

    newCost = calculateErrorOnIthRowCol(boxesToCheck[0][0],
                                        boxesToCheck[0][1],
                                        newSudoku) + calculateErrorOnIthRowCol(boxesToCheck[1][0],
                                                                               boxesToCheck[1][1],
                                                                               newSudoku)
    # currentCost = costFunction(currentSudoku)
    # newCost = costFunction(newSudoku)
    costDifference = newCost - currentCost
    rho = math.exp(-costDifference / sigma)

    if (np.random.uniform(1, 0, 1) < rho):
        return ([newSudoku, costDifference])

    return ([currentSudoku, 0])


def maximumNumberOfIterationsRequired(startingSudoku):
    numberOfIterations = 0
    for i in range(0, 9):
        for j in range(0, 9):
            if startingSudoku[i, j] != 0:
                numberOfIterations += 1
    return numberOfIterations


def CalculateInitialSigma(sudoku, fixedSudoku, listOfBlocks):
    listOfDifferences = []
    currentSudokuCertificate = sudoku
    for i in range(1, 10):
        currentSudokuCertificate = generateNewSudokuCertificate(currentSudokuCertificate, fixedSudoku, listOfBlocks)[0]
        listOfDifferences.append(costFunction(currentSudokuCertificate))
    return (statistics.pstdev(listOfDifferences))


def solveSudoku(sudoku):

    f = open("demofile2.txt", "a")
    solutionFound = 0

    while (solutionFound == 0):

        decreaseFactor = 0.99
        stuckCount = 0
        fixedSudoku = np.copy(sudoku)
        printSudoku(sudoku)
        identifyFixedSudokuValues(fixedSudoku)
        listOfBlocks = createList3x3Blocks()
        currentSudokuCertificate = fillNondeterministically3x3Blocks(sudoku, listOfBlocks)
        sigma = CalculateInitialSigma(sudoku, fixedSudoku, listOfBlocks)
        score = costFunction(currentSudokuCertificate)
        numberOfIterations = maximumNumberOfIterationsRequired(fixedSudoku)

        if score <= 0:
            solutionFound = 1

        while solutionFound == 0:

            previousScore = score

            for i in range(0, numberOfIterations):

                newState = ChooseNewState(currentSudokuCertificate, fixedSudoku, listOfBlocks, sigma)
                currentSudokuCertificate = newState[0]
                scoreDiff = newState[1]
                score += scoreDiff
                print(score)
                f.write(str(score) + '\n')

                if score <= 0:
                    solutionFound = 1
                    break

            sigma *= decreaseFactor

            if score <= 0:
                solutionFound = 1
                break

            if score >= previousScore:
                stuckCount += 1
            else:
                stuckCount = 0

            if (stuckCount > 80):
                sigma += 2

            if (costFunction(currentSudokuCertificate) == 0):
                printSudoku(currentSudokuCertificate)
                break

    f.close()
    return (currentSudokuCertificate)


solution = solveSudoku(sudoku)
print(costFunction(solution))
printSudoku(solution)