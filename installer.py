import subprocess, os

komennot = ["curl https://github.com/paukkle/Hirviopeli/archive/main.zip -O .\hirviopeli.zip",
    "Expand-Archive -LiteralPath .\hirviopeli.zip -DestinationPath .\ -Force",
    "Get-ChildItem -Path .\Hirviopeli-main | Copy-Item -Destination .\ -Force -Recurse",
    "Remove-Item .\Hirviopeli-main -Recurse",
    "Remove-Item .\*.* -Exclude *.exe"]

with open("installer.ps1", "w") as file:
    for i, komento in enumerate(komennot):
        if i != len(komennot) -1:
            file.write(komento + "\n")
        else:
            file.write(komento)

subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "./installer.ps1"])