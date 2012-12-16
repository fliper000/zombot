class UserPrompt(object):

    def prompt_user(self, prompt_string, choice):
        prompt_string += '\n' + "\n".join(
            [str(index + 1) + ": " + option
             for index, option in enumerate(choice)])
        selected_index = -1
        while not selected_index in range(len(choice)):
            try:
                selected_index = int(raw_input(prompt_string + "\n")) - 1
            except ValueError:
                pass
        selected = choice[selected_index]
        print "You selected " + selected
        return selected
