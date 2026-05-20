from prompt_toolkit import prompt, print_formatted_text
from prompt_toolkit.formatted_text import HTML

# input a simple value
value = ''
while True:
    value = prompt("Your name: ", default=value).strip()
    if not value:
        continue
    print_formatted_text(HTML(f"You entered: \n<ansiblue>{value}</ansiblue>"))
    if prompt("Is this correct? [Y/n]").lower() in ("", "y", "yes"):
        break
print_formatted_text(HTML(f"So your name is: <ansiblue>{value}</ansiblue>"))

# input a multi-line value
print()
value = ''
while True:
    value = prompt(
        "Your run description: (Shift-Enter to enter)\n",
        default=value,
        multiline=True,
    ).strip()
    if not value:
        continue
    print_formatted_text(HTML(f"You entered: \n<ansiblue>{value}</ansiblue>"))
    if prompt("Is this correct? [Y/n]").lower() in ("", "y", "yes"):
        break
print_formatted_text(HTML(f"So the description is:\n<ansiblue>{value}</ansiblue>"))
