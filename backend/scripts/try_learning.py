"""Run a local Pattern Drill session with AI-generated exercises."""

from openai import OpenAIError

from app.core.learning import generate_exercises


def main():
    pattern = "I'd like to go to {place}."
    exercise_count = 5

    try:
        exercises = generate_exercises(pattern, exercise_count)
    except ValueError as error:
        print("Could not create the exercise set: " + str(error))
        return
    except OpenAIError as error:
        print("The OpenAI request failed. Check the API key, billing, and model access.")
        print("Error type: " + error.__class__.__name__)
        return
    except (KeyError, TypeError):
        print("The API response could not be read. Please try again.")
        return

    print("\nPattern: " + pattern)
    print("Generated " + str(len(exercises)) + " exercises.\n")

    for exercise in exercises:
        print("Exercise " + str(exercise["number"]) + "/" + str(len(exercises)))
        print(exercise["prompt"])
        input("Press Enter to reveal the reference answer...")
        print("Reference answer: " + exercise["answer"] + "\n")

        if exercise["number"] < len(exercises):
            action = input("Press Enter for the next exercise, or q to quit: ")
            if action.strip().lower() == "q":
                break

    print("Session finished.")


if __name__ == "__main__":
    main()
