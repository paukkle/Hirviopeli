curl https://github.com/paukkle/Hirviopeli/archive/main.zip -O .\hirviopeli.zip
Expand-Archive -LiteralPath .\hirviopeli.zip -DestinationPath .\ -Force
Get-ChildItem -Path .\Hirviopeli-main | Copy-Item -Destination .\ -Force -Recurse
Remove-Item .\Hirviopeli-main -Recurse
Remove-Item .\*.* -Exclude *.exe