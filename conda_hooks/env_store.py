import subprocess


def main():
    output = (
        subprocess.check_output(["mamba", "env", "export", "--from-history"])
        .decode()
        .strip()
        .splitlines()
    )
    with open("environment.yml", "w") as fptr:
        for line in output:
            if line.startswith("prefix:"):
                continue
            fptr.write(line + "\n")


if __name__ == "__main__":
    main()
