from sys import argv

from executor_exporter.exporter import metrics


def update_readme_metrics(readme_path):
    columns = ("Name", "Type", "Labels", "Description")
    sep = " | "

    table_lines = [sep.join(columns), sep.join(["---"] * len(columns))]
    for metric in metrics:
        table_lines.append(
            sep.join(
                (
                    metric._name,
                    metric._type,
                    ", ".join(metric._labelnames),
                    metric._documentation,
                )
            )
        )

    readme_lines = []
    with open(readme_path) as readme_file:
        for lineno, line in enumerate(readme_file.readlines()):
            if "metrics:begin" in line:
                begin = lineno
            elif "metrics:end" in line:
                end = lineno

            readme_lines.append(line)

    readme_lines = [
        *readme_lines[: begin + 1],
        "\n".join(table_lines) + "\n",
        *readme_lines[end:],
    ]
    with open(readme_path, "w") as readme_file:
        readme_file.writelines(readme_lines)


if __name__ == "__main__":
    readme_path = argv[1]
    update_readme_metrics(readme_path)
