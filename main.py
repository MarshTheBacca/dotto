from utils import (SCORES_PATH, Game, SettingsData, get_valid_int, import_2d,
                   show_scores)


def main() -> None:
    settings = SettingsData()
    while True:
        print("===========================\n     Welcome To Dotto!     \n===========================")
        option = get_valid_int("What would you like to do?\n1) Play\n2) Settings\n3) View Scores\n4) Exit\n", 1, 4)
        if option == 1:
            game = Game(settings)
            game.play()
        elif option == 2:
            settings.edit()
        elif option == 3:
            show_scores(import_2d(SCORES_PATH))
        elif option == 4:
            break


if __name__ == "__main__":
    main()
