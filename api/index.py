import requests
import random
from flask import Flask, jsonify, request
import json
import os
import base64

class GameInfo:
    def __init__(self):
        self.TitleId: str = "10D787"
        self.SecretKey: str = "QDNIYMENSJRYO1P1DE38W786HPY8CHAZCOXFNPBF18NCSHHWP"
        self.ApiKey: str = "OC|1277417425448465|162f41a23ef31c3da7cf1d999c4b0c85"

    def get_auth_headers(self):
        return {"content-type": "application/json", "X-SecretKey": self.SecretKey}

settings = GameInfo()
app = Flask(__name__)

def ReturnFunctionJson(data, funcname, funcparam={}):
    rjson = data["FunctionParameter"]
    userId: str = rjson.get("CallerEntityProfile").get("Lineage").get(
        "TitlePlayerAccountId")

    req = requests.post(
        url=f"https://{settings.10D787}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers=settings.GetAuthHeaders())

    if req.status_code == 200:
        return jsonify(
            req.json().get("data").get("FunctionResult")), req.status_code
    else:
        return jsonify({}), req.status_code


def GetIsNonceValid(nonce: str, oculusId: str):
    req = requests.post(
        url=f'https://graph.oculus.com/user_nonce_validate?nonce=' + nonce +
        '&user_id=' + oculusId + '&access_token=' + settings.ApiKey,
        headers={"content-type": "application/json"})
    return req.json().get("is_valid")


def Validate_Orgscoped_Id(orgscope: str) -> bool:
    """Validate Oculus orgscoped ID"""
    try:
        res = requests.get(url=f"https://graph.oculus.com/{orgscope}?access_token={settings.ApiKey}")
        data = res.json()
        if data.get("id") == orgscope:
            print("Orgscope Id Valid")
            return True
        return False
    except:
        return False

# Funny Lil Youtube Embed Webpage For You Fellas
@app.route("/", methods=["GET"])
def main():
    image_url = "https://youtu.be/lK0sUU0K5SY?si=RAD-aQ-N4XTg5BKC"
    
    
    def get_youtube_embed_url(url):
        if "youtube.com/watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}?autoplay=1"
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}?autoplay=1"
        return None
    
    
    def get_discord_media_url(url):
        if "discord.com/attachments/" in url or "cdn.discordapp.com/attachments/" in url:
            return url
        return None
    
    youtube_embed = get_youtube_embed_url(image_url)
    discord_media = get_discord_media_url(image_url)
    
    if youtube_embed:
        media_element = f'<iframe src="{youtube_embed}" allowfullscreen></iframe>'
    else:
        
        media_element = f'<img src="{image_url}" alt="Media Content" />'
    
    return f"""
    <html>
      <head>
        <title></title>
        <style>
          body {{
            background-color: #111;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
          }}
          img, iframe {{
            max-width: 90vw;
            max-height: 90vh;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
            border: none;
          }}
          iframe {{
            width: 80vw;
            height: 45vw;
            max-height: 80vh;
          }}
        </style>
      </head>
      <body>
        {media_element}
      </body>
    </html>
    """

# Replace https://auth-prod.gtag-cf.com/api/PlayFabAuthentication with this endpoint
@app.route("/api/PlayFabAuthentication", methods=["POST", "GET"])
def playfab_authentication():
    if request.method == "GET":
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    rjson = request.get_json()
    
    
    custom_id = rjson.get("CustomId")
    app_id = rjson.get("AppId")
    nonce = rjson.get("Nonce")
    oculus_id = rjson.get("OculusId")
    platform = rjson.get("Platform")
    app_version = rjson.get("AppVersion")

   
    user_agent = request.headers.get('User-Agent', '')
    if "UnityPlayer" not in user_agent:
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    
    if not custom_id or not custom_id.startswith("OCULUS"):
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    if not app_id or app_id != settings.TitleId:
        return jsonify({
            "Message": "Request sent for the wrong App ID",
            "Error": "BadRequest-AppIdMismatch",
        }), 400

    if not nonce:
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    if not oculus_id:
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    if platform != "Quest":
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    if app_version == "-1":
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

   
    try:
        nonce_response = requests.post(
            url=f"https://graph.oculus.com/user_nonce_validate",
            json={
                "access_token": settings.ApiKey,
                "nonce": nonce,
                "user_id": oculus_id
            },
            headers={"content-type": "application/json"}
        )
        
        if nonce_response.status_code != 200 or not nonce_response.json().get("is_valid", False):
            return jsonify({
                "BanMessage": "Your account has been traced and you have been banned.",
                "BanExpirationTime": "Indefinite"
            }), 403
    except:
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

   
    if not Validate_Orgscoped_Id(oculus_id):
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

   
    url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId"
    login_request = requests.post(
        url=url,
        json={
            "ServerCustomId": custom_id,
            "CreateAccount": True,
        },
        headers=settings.get_auth_headers(),
    )

    if login_request.status_code == 200:
        data = login_request.json().get("data")
        session_ticket = data.get("SessionTicket")
        entity_token = data.get("EntityToken").get("EntityToken")
        playfab_id = data.get("PlayFabId")
        entity_type = data.get("EntityToken").get("Entity").get("Type")
        entity_id = data.get("EntityToken").get("Entity").get("Id")

       
        link_response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/LinkServerCustomId",
            json={
                "ForceLink": True,
                "PlayFabId": playfab_id,
                "ServerCustomId": custom_id,
            },
            headers=settings.get_auth_headers(),
        ).json()

        return jsonify({
            "PlayFabId": playfab_id,
            "SessionTicket": session_ticket,
            "EntityToken": entity_token,
            "EntityId": entity_id,
            "EntityType": entity_type,
        }), 200
    else:
        if login_request.status_code == 403:
            ban_info = login_request.json()
            if ban_info.get("errorCode") == 1002:
                ban_message = ban_info.get("errorMessage", "Your account has been traced and you have been banned.")
                ban_details = ban_info.get("errorDetails", {})
                ban_expiration_key = next(iter(ban_details.keys()), None)
                ban_expiration_list = ban_details.get(ban_expiration_key, [])
                ban_expiration = (
                    ban_expiration_list[0]
                    if len(ban_expiration_list) > 0
                    else "Indefinite"
                )
                print(ban_info)
                return jsonify({
                    "BanMessage": ban_message,
                    "BanExpirationTime": ban_expiration,
                }), 403
            else:
                error_message = ban_info.get(
                    "errorMessage", "Your account has been traced and you have been banned."
                )
                return jsonify({
                    "BanMessage": error_message,
                    "BanExpirationTime": "Indefinite"
                }), 403
        else:
            return jsonify({
                "BanMessage": "Your account has been traced and you have been banned.",
                "BanExpirationTime": "Indefinite"
            }), 403

# Replace https://auth-prod.gtag-cf.com/api/CachePlayFabId with this endpoint
@app.route("/api/CachePlayFabId", methods=["POST"])
def cache_playfab_id():
    return jsonify({"Message": "Success"}), 200


# Replace https://title-data.gtag-cf.com with this endpoint
@app.route('/api/TitleData', methods=['POST', 'GET'])
def titledata():
    response_data = {
        "AutoMuteCheckedHours": {
            "hours": 169
        },
        "AutoName_Adverbs": [
            "Cool", "Fine", "Bald", "Bold", "Half", 
            "Only", "Calm", "Fab", "Ice", "Mad", 
            "Rad", "Big", "New", "Old", "Shy"
        ],
        "AutoName_Nouns": [
            "Gorilla", "Chicken", "Darling", "Sloth", "King", 
            "Queen", "Royal", "Major", "Actor", "Agent", 
            "Elder", "Honey", "Nurse", "Doctor", "Rebel", 
            "Shape", "Ally", "Driver", "Deputy"
        ],
        "BundleBoardSign": "<color=#ff4141>DISCORD.GG/YOURSERVER</color>",
        "BundleKioskButton": "<color=#ff4141>DISCORD.GG/YOURSERVER</color>",
        "BundleKioskSign": "<color=#ff4141>DISCORD.GG/YOURSERVER</color>",
        "BundleLargeSign": "<color=#ff4141>DISCORD.GG/YOURSERVER</color>",
        "EmptyFlashbackText": "FLOOR TWO NOW OPEN\n FOR BUSINESS\n\nSTILL SEARCHING FOR\nBOX LABELED 2021",
        "EnableCustomAuthentication": True,
        "GorillanalyticsChance": 4320,
        "LatestPrivacyPolicyVersion": "2024.09.20",
        "LatestTOSVersion": "2024.09.20",
        "MOTD": "<color=#ac1a00>WELCOME TO YOUR GAME NAME!</color>\n\n\n<color=#0099c2>BOOST DISCORD.GG/YOURSERVER FOR EVERY COSMETIC!</color>\n\n\n<color=#cacfd2>CREDITS: FLYINGACT</color>\n\n<color=#41ff80>THIS GAME TAKES YOU INTO OLDER AND NEWER GTAG UPDATES!</color>",
        "SeasonalStoreBoardSign": "<color=#ff7241>FALL!</color>",
        "TOS_2024.09.20": "DISCORD.GG/YOURSERVER",
        "TOBAlreadyOwnCompTxt": "DISCORD.GG/YOURSERVER",
        "TOBAlreadyOwnPurchaseBundle": "YOUR GAME NAME",
        "TOBDefCompTxt": "DISCORD.GG/YOURSERVER",
        "TOBDefPurchaseBtnDefTxt": "YOUR GAME NAME",
        "UseLegacyIAP": False
        
    }
    return jsonify(response_data)

# Replace https://iap.gtag-cf.com/api/ConsumeOculusIAP with this endpoint
@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_oculus_iap():
    rjson = request.get_json()

    access_token = rjson.get("userToken")
    user_id = rjson.get("userID")
    nonce = rjson.get("nonce")
    sku = rjson.get("sku")

    response = requests.post(
        url=f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"},
    )

    if response.json().get("success"):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})

@app.route("/api/GetAcceptedAgreements", methods=['POST', 'GET'])
def GetAcceptedAgreements():
  data = request.json

  return jsonify({"PrivacyPolicy":"1.1.28","TOS":"11.05.22.2"}), 200

@app.route("/api/SubmitAcceptedAgreements", methods=['POST', 'GET'])
def SubmitAcceptedAgreements():
  data = request.json

  return jsonify({}), 200

@app.route("/api/ConsumeCodeItem", methods=["POST"])
def consume_code_item():
    rjson = request.get_json()
    code = rjson.get("itemGUID")
    playfab_id = rjson.get("playFabID")
    session_ticket = rjson.get("playFabSessionTicket")

    if not all([code, playfab_id, session_ticket]):
        return jsonify({"error": "Missing parameters"}), 400

    raw_url = f"https://github.com/redapplegtag/backendsfrr" # make a github and put the raw here (Redeemed = not redeemed, u have to add discord webhookss and if your smart you can make it so it auto updates the github url (redeemed is not redeemed, AlreadyRedeemed is already redeemed, then dats it
    # code:Redeemed 
    response = requests.get(raw_url)

    if response.status_code != 200:
        return jsonify({"error": "GitHub fetch failed"}), 500

    lines = response.text.splitlines()
    codes = {split[0].strip(): split[1].strip() for line in lines if (split := line.split(":")) and len(split) == 2}

    if code not in codes:
        return jsonify({"result": "CodeInvalid"}), 404

    if codes[code] == "AlreadyRedeemed":
        return jsonify({"result": codes[code]}), 200

    grant_response = requests.post(
        f"https://{settings.TitleId}.playfabapi.com/Admin/GrantItemsToUsers",
        json={
            "ItemGrants": [
                {
                    "PlayFabId": playfab_id,
                    "ItemId": item_id,
                    "CatalogVersion": "DLC"
                } for item_id in ["dis da cosmetics", "anotehr cposmetic", "anotehr"]
            ]
        },
        headers=settings.get_auth_headers()
    )


    if grant_response.status_code != 200:
        return jsonify({"result": "PlayFabError", "errorMessage": grant_response.json().get("errorMessage", "Grant failed")}), 500

    new_lines = [f"{split[0].strip()}:AlreadyRedeemed" if split[0].strip() == code else line.strip() 
             for line in lines if (split := line.split(":")) and len(split) >= 2]

    updated_content = "\n".join(new_lines).strip()

    return jsonify({"result": "Success", "itemID": code, "playFabItemName": codes[code]}), 200

@app.route('/api/v2/GetName', methods=['POST', 'GET'])
def GetNameIg():
    return jsonify({"result": f"GORILLA{random.randint(1000,9999)}"})

# Put your backend URL with this endpoint /api/photon into your photon and photon voice custom server!
@app.route("/api/photon", methods=["POST", "GET"])
def photonauth():
    if request.method == "GET":
        userid = request.args.get("username")
        token = request.args.get("token")

        if not userid or not token:
            return jsonify({
                "message": "Missing required parameters",
                "userid": None,
                "resultCode": 0,
                "nickname": None,
            }), 400

        account_valid = CheckUserAccount(userid)

        if account_valid:
            return jsonify({
                "message": f"Authenticated user {userid} with token {token}, for title {settings.TitleId}",
                "userid": userid,
                "resultCode": 1,
                "nickname": None,
            }), 200
        else:
            return jsonify({
                "message": f"Failed to authenticate user {userid} with token {token}, for title {settings.TitleId}",
                "userid": userid,
                "resultCode": 0,
                "nickname": None,
            }), 200

    elif request.method == "POST":
        rjson = request.get_json()
        
        platform = rjson.get("Platform")
        app_id = rjson.get("AppId")
        app_version = rjson.get("AppVersion")
        session_ticket = rjson.get("Ticket")
        oculus_id = request.args.get("OculusId")
        nonce = request.args.get("Nonce")
        username = request.args.get("username")

        if not session_ticket or "-" not in session_ticket:
            return jsonify({
                "message": "Invalid session ticket",
                "userid": None,
                "resultCode": 2,
                "nickname": None,
            }), 400

        user_id = session_ticket.split("-")[0]

        if len(user_id) != 16:
            return jsonify({
                "message": "Invalid token",
                "userid": None,
                "resultCode": 2,
                "nickname": None,
            }), 400

        if app_id != settings.TitleId:
            return jsonify({
                "message": f"Failed to authenticate user {username} with token {session_ticket}, for title {settings.TitleId}",
                "userid": user_id,
                "resultCode": 3,
                "nickname": None,
            }), 403

        if platform != "Quest":
            return jsonify({
                "message": f"Failed to authenticate user {username} with token {session_ticket}, for title {settings.TitleId}",
                "userid": user_id,
                "resultCode": 3,
                "nickname": None,
            }), 403

        req = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": user_id},
            headers=settings.get_auth_headers()
        )

        if req.status_code == 200:
            nickname = req.json().get("data", {}).get("UserInfo", {}).get("TitleInfo", {}).get("DisplayName")
            
            return jsonify({
                "message": f"Authenticated user {username} with token {session_ticket}, for title {settings.TitleId}",
                "userid": user_id.upper(),
                "resultCode": 1,
                "nickname": nickname,
            }), 200
        else:
            return jsonify({
                "message": "Something went wrong",
                "userid": None,
                "resultCode": 0,
                "nickname": None,
            }), 200
    else:
        return jsonify({
            "message": f"Use a POST or GET Method instead of {request.method.upper()}"
        }), 405

def ReturnFunctionJson(data, funcname, funcparam={}):
    print(f"Calling function: {funcname} with parameters: {funcparam}")
    rjson = data.get("FunctionParameter", {})
    userId = rjson.get("CallerEntityProfile",
                       {}).get("Lineage", {}).get("TitlePlayerAccountId")

    print(f"UserId: {userId}")

    req = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers={
            "content-type": "application/json",
            "X-SecretKey": secretkey
        })

    if req.status_code == 200:
        result = req.json().get("data", {}).get("FunctionResult", {})
        print(f"Function result: {result}")
        return jsonify(result), req.status_code
    else:
        print(f"Function execution failed, status code: {req.status_code}")
        return jsonify({}), req.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080) # 
