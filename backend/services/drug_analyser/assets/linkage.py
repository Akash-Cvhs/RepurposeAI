url = "https://akashsubramanis-team.adalo.com/drug"
response = reversed.post(url, json={"DRUG"})
print(response.json())
