import os               
import json                   
import random 
import requests          
import csv              
import html 

# This is instead of simply using something like:
# resp_data = resp.json() 
# or
# resp_data = json.loads(resp.text)

#########



##### IMPORTANT #####

# When you are specifying the category parameter in your API requests, you can't provide
# the name of the category, instead you need to use the API's corresponding category number.

# For example, if the user wants a question from the "Sports" category, you can't say
# "category=Sports" in your API request. Instead, you need to say something like
# "category=21" because the Sports category's number is 21 according to the map below.

# You should use the following dictionary to take the category that your user selects
# in each round and find the corresponding API category number to use in your API request.

api_category_map = {
        "Any Category": "any",
        "General Knowledge": "9",
        "Entertainment: Books": "10",
        "Entertainment: Film": "11",
        "Entertainment: Music": "12",
        "Entertainment: Musicals & Theatres": "13",
        "Entertainment: Television": "14",
        "Entertainment: Video Games": "15",
        "Entertainment: Board Games": "16",
        "Science & Nature": "17",
        "Science: Computers": "18",
        "Science: Mathematics": "19",
        "Mythology": "20",
        "Sports": "21",
        "Geography": "22",
        "History": "23",
        "Politics": "24",
        "Art": "25",
        "Celebrities": "26",
        "Animals": "27",
        "Vehicles": "28",
        "Entertainment: Comics": "29",
        "Science: Gadgets": "30",
        "Entertainment: Japanese Anime & Manga": "31",
        "Entertainment: Cartoon & Animations": "32",
    }

#shows answer choices 
def display(game_difficulty, results):
        if game_difficulty == "hard":
                return
        elif game_difficulty == "easy":
                mylist = [results["correct_answer"], random.choice(results["incorrect_answers"])]
        else: #medium
                mylist = [results["correct_answer"]] + results["incorrect_answers"]
        print("\nAnswer Choices:")
        random.shuffle(mylist)
        for i in range(len(mylist)):
                print(chr(i + 65), ". ", mylist[i], sep='')
        print("Please enter the letter corresponding to your answer choice.")
        return mylist

def correct_answer_check(game_difficulty, user_answer, results, mylist):
        if game_difficulty == 'hard':
                return user_answer.lower() == results["correct_answer"].lower()
        else:
                try:
                        return mylist[ord(user_answer) - 65] == results["correct_answer"]
                except:
                        print("You did not enter a valid character answer choice!")
                        return False

#determine score for current round
def round_scoring(question_difficulty, correct_check):
        round_score = 0
        if correct_check:
                if question_difficulty == "easy":
                        round_score = 10
                elif question_difficulty == "medium":
                        round_score = 20
                else:
                        round_score = 30
                print("Correct! You must be a genius! You earned", round_score, "points for getting a", question_difficulty, "question.")
        else:
                if question_difficulty == "easy":
                        round_score = -5
                elif question_difficulty == "medium":
                        round_score = -10
                else:
                        round_score = -15
                print("Incorrect...you'll do better next time! You lost", 0 - round_score, "points for missing a", question_difficulty, "question.")
                # print("The correct answer for this question was: ", results["correct_answer"], ".", sep='')
        return round_score

#determine scaled score after game is finished
def scaled(game_difficulty, game_score):
        scaled_score = game_score
        if game_difficulty == "medium":
                scaled_score *= 2
        elif game_difficulty == "hard":
                scaled_score *= 3
        return scaled_score

def main():
        directory = "/Users/corannejuang/Desktop/PyCode/trivia_question/"
        filename = input("What is the name of the configuration file you would like to use? \n> ")
        print()
        directory += filename; #directory in Finder
        rows = [] #used to write to csv file later

        #try opening file, otherwise print error message and exit program
        try:
                file = open(filename)
                data = json.load(file)
        except:
                print("Oh no! The configuration file, ", filename, " does not exist. We will now be exiting the game.", sep='')
                exit()

        #try reading in rounds as int, otherwise print error message and default rounds = 2
        try:
                rounds = int(data["num_rounds"])
                #check if rounds is within bounds
                if (rounds > 15 or rounds < 1):
                        print("Oh no! The number of rounds provided, ", rounds,  ", is outside of the bounds. But dont worry! We will use the default number of rounds, 2.\n", sep='')
                        rounds = 2
        except:
                rounds = data["num_rounds"]
                print("Oh no! The number of rounds provided, ", rounds,  ", is not an integer. But dont worry! We will use the default number of rounds, 2.\n", sep='')
                rounds = 2

        #read in potential categories
        categories = data["potential_categories"]
        if not categories: 
                print("Oh no! The potential categories list provided, [], is empty. But dont worry! We will use the default potential category list, ['Art', 'Animals', 'Vehicles']\n",)
                categories = ["Art", "Animals","Vehicles"]

        #read in game difficulty
        game_difficulty = data["game_difficulty"].lower()
        if game_difficulty != "easy" and game_difficulty != "medium" and game_difficulty != "hard":
                print("Oh no! The game difficulty provided, ", game_difficulty, 
                        ", is invalid. But dont worry! We will use the default game difficulty, 'medium'. Hopefully you didn't choose 'easy' or this may be a challenge for you!\n", sep='')
                game_difficulty = "medium"

        #read in game summary filename
        summary_filename = data["game_summary_filename"]
        if len(summary_filename) == 0 or summary_filename[-4:] != ".csv":
                print("The game summary filename provided, ", summary_filename, 
                        ", is invalid. Using the default game summary filename, 'game_summary_default.csv'.\n", sep='')
                summary_filename = "game_summary_default.csv"

        #print game config settings
        print("#### Game-Level Configuration Settings ####")
        print("Number of Rounds:", rounds)
        print("Potential Categories:", categories)
        print("Game Difficulty:", game_difficulty)
        print("Game Summary Filename:", summary_filename)

        print("\nSomething to note before you start the game...")
        print("You will need to choose the question difficulty for every round and you will be penalized and rewarded points with respect to the difficulty you choose.")
        print("The points are allocated as shown below:")
        print("-----------------------------------")
        print("|________|__correct__|__incorrect__|")
        print("|__easy__|____10_____|_____-5______|")
        print("|_medium_|____20_____|_____-10_____|")
        print("|__hard__|____30_____|_____-15_____|")
        print("-----------------------------------")
        print("\nLet's play the game!")
        #run the game 
        game_score = 0
        for i in range(rounds):
                correct = False;
                round_score = 0
                print("\n############ Round Number ", i + 1, " ############", '\n', sep='')
                print("Categories:")
                for j in range(len(categories)):
                        print((j + 1), "-", categories[j])

                #prompt user to choose a category
                #try reading in category_num as int, otherwise print error message and default category_num = 1
                print("\nChoose a category number for Round ", i + 1, ". You may enter any of the following numbers: ",
                        [item for item in range(1, len(categories) + 1)], sep='')
                try:
                        category_num = int(input("> "))
                        if category_num not in range(1, len(categories) + 1):
                                print("\nOh no! The category number provided is not within range! But don't worry! We will use the default choice of Category 1.")
                                category_num = 1
                except:
                        # category_num = input("> ")
                        print("\nOh no! The category number provided is not an integer! But don't worry! We will use the default choice of Category 1.")
                        category_num = 1

                question_category = api_category_map[categories[category_num - 1]]

                #prompt user to choose question difficulty
                print("\nChoose the question difficulty you would like to use for the Round ", i + 1, ' ', 
                        categories[category_num - 1], " Category question. You may enter 'easy', 'medium', or 'hard'.", sep='')
                question_difficulty = input("> ").lower()
                if question_difficulty != "easy" and question_difficulty != "medium" and question_difficulty != "hard":
                        print("\nOh no! The game difficulty provided, ", question_difficulty, 
                                ", is invalid. But dont worry! We will use the default question difficulty, 'medium'. Hopefully you didn't choose 'easy' or this may be a challenge for you!\n", sep='')
                        question_difficulty = "medium"

                #get requests from api
                parameters = {
                        "amount": 1,
                        "category": question_category,
                        "difficulty": question_difficulty,
                        "type": "multiple"
                }
                try: 
                        response = requests.get(url="https://opentdb.com/api.php", params=parameters)
                        response.raise_for_status()
                        # resp_data = json.loads(response.text)
                        resp_data = json.loads(html.unescape(response.text))
                        response_code = resp_data["response_code"]
                        if response_code != 0:
                                print("API was unable to handle the request")
                                continue
                        results = resp_data["results"][0]
                except:
                        print("API was not able to return a valid response. Moving on to the next round.")
                        continue

                #display the question API generated
                print("\n...are...you...READY?")
                print("\nHere's your question:", results["question"])
                #display answer choices depending on game difficulty
                mylist = display(game_difficulty, results)

                #prompt user for their answer to the question
                print("\nEnter your answer champ: ")
                user_answer = input("> ")
                print()

                #determine score for current round
                round_score = round_scoring(question_difficulty, correct_answer_check(game_difficulty, user_answer, results, mylist))

                #if answered correctly
                if round_score > 0:
                        correct = True
                else:
                        if game_difficulty != 'hard':
                                print("The correct answer for this question was: ", chr(mylist.index(results["correct_answer"]) + 65), ". ", results["correct_answer"], ".", sep='')
                        else:
                                print("The correct answer for this question was: ", results["correct_answer"], ".", sep='')

                #update total game score
                game_score += round_score
                print("\nYour current total score is:", game_score)
                #create row for that round's data and append to list that stores every rounds data
                row = [i + 1, question_category, question_difficulty, results["question"], user_answer, results["correct_answer"], correct, round_score]
                rows.append(row)


        scaled_score = scaled(game_difficulty, game_score)
        #write to csvfile
        with open(summary_filename, 'w') as csvfile: 
                writer = csv.writer(csvfile)
                writer.writerow(['rducound_number', 'question_category', 'question_difficulty', 'question_text', 'user_answer', 
                        'correct_answer', 'correct', 'unscaled_points_earned'])
                writer.writerows(rows)
                writer.writerow(['', '', '', '', '', '', "Total Game Score (Unscaled):", game_score])
                writer.writerow(['', '', '', '', '', '', "Total Game Score (Scaled):", scaled_score])

        #print end of game message
        print("\n##################################################")
        print("GOOD GAME! Thanks for playing!\n")
        print("Here are your overall scores: ")
        print("Unscaled Game Score:", game_score)
        print("Scaled Game Score:", scaled_score)
        print("If you're interested in your game summary (which contains the correct answers) visit the", summary_filename, "file inside of the game_summary_files directory.")
        
        #close files 
        file.close()

if __name__ == "__main__":
        main()

























