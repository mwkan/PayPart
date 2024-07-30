import requests
import json
import uuid
import re

# endpoints
token_endpoint = "https://ob.sandbox.natwest.com/token"
VRP_consent_endpoint = "https://ob.sandbox.natwest.com/open-banking/v3.1/pisp/domestic-vrp-consents"
payment_endpoint = "https://ob.sandbox.natwest.com/open-banking/v3.1/pisp/domestic-vrps"

# environment variables
client_id = "QdWMOwmqVtVXZlFAD_mI5CyRdGQD4J58BYduuIkxZzg%3D"
client_secret = "__yi_l6ny7Nsa7GjM32e3baiIghwdAG_CoRKRhPTH-s%3D"

# dictionary of our sample customer usernames and account numbers, this would be a further API call but due to time this is hard coded
sample_data = {
    "djefferson@hackathon-team.2024.co.uk": 50000011223301,
    "jpeterson@hackathon-team.2024.co.uk": 50000011223401,
    "alicesmith@hackathon-team.2024.co.uk": 50000011223777,
    "alanarnold@hackathon-team.2024.co.uk": 50000011246245,
    "louisesmith@hackathon-team.2024.co.uk": 50000012132301
}

# 1. get access token

def get_access_token(scope):
    payload = 'grant_type=client_credentials&client_id={}&client_secret={}&scope={}'.format(client_id, client_secret,
                                                                                            scope)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", token_endpoint, headers=headers, data=payload)
    print("get_access_token call status:", response.status_code)
    print("access_token:", response.json()['access_token'])
    return response


# 2. create a VRP consent

def VRP_consent(amount_to_pay_per_user, access_token):
    payload = json.dumps({
        "Data": {
            "ControlParameters": {
                "VRPType": [
                    "UK.OBIE.VRPType.Other"
                ],
                "PSUAuthenticationMethods": [
                    "UK.OBIE.SCANotRequired"
                ],
                "VRPSubType": [
                    "UK.NWG.VRPSubType.Single"
                ],
                "InitialPayment": {
                    "Amount": "{}".format(amount_to_pay_per_user),
                    "Currency": "GBP"
                }
            },
            "Initiation": {
                "CreditorAccount": {
                    "SchemeName": "SortCodeAccountNumber",
                    "Identification": "50499910000998",
                    "Name": "powered by PayPart",
                    "SecondaryIdentification": "secondary-identif"
                }
            }
        },
        "Risk": {}
    })
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'x-fapi-financial-id': '0015800000jfwxXAAQ',
        'Content-Type': 'application/json',
        'x-jws-signature': 'DUMMY_SIG',
        'x-idempotency-key': '{}'.format(uuid.uuid4())
    }

    response = requests.request("POST", VRP_consent_endpoint, headers=headers, data=payload)

    print("VRP call status:", response.status_code)
    print("consent_id:", response.json()['Data']['ConsentId'])
    return response


# 3. redirect customer to approve a VRP consent
def get_consent(authorization, consent_id, username):
    #for the username, we need to get account number. This is where we would want to do another api call but we will retrieve from dictionary

    account_number = sample_data.get(username)

    url = "https://api.sandbox.natwest.com/authorize?" \
          "client_id={}&" \
          "response_type=code id_token&" \
          "scope=openid payments&" \
          "redirect_uri=https://payment.natwestpayit.com/status&" \
          "state=ABC" \
          "&request={}" \
          "&authorization_mode=AUTO_POSTMAN" \
          "&authorization_username={}" \
          "&authorization_account={}&" \
          "authorization_result={}".format(client_id, consent_id, username, account_number, authorization)

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    print("get_consent status code", response.status_code)
    # print(response.text)
    url_link = response.json()['redirectUri']
    get_code = re.search(r'code=([a-f0-9-]+)', url_link)
    print(get_code.group(1))
    return response


# 4. exchange authorisation code for access token specific to VRP request

def exchange_code_for_token(code):
    payload = 'client_id={}' \
              '&client_secret={}' \
              '&redirect_uri=https%3A%2F%2Fpayment.natwestpayit.com%2Fstatus' \
              '&grant_type=authorization_code' \
              '&code={}'.format(client_id, client_secret, code)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", token_endpoint, headers=headers, data=payload)
    print("exchange_code_call:", response.status_code)
    print("new_access_token:", response.json()['access_token'])
    return response


# 5. Confirm customer has available funds

def confirm_funds(consent_id, access_token, amount):
    payload = json.dumps({
        "Data": {
            "ConsentId": "{}".format(consent_id),
            "Reference": "Tools",
            "InstructedAmount": {
                "Amount": "{}".format(amount),
                "Currency": "GBP"
            }
        },
        "Risk": {}
    })
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'x-fapi-financial-id': '0015800000jfwxXAAQ',
        'Content-Type': 'application/json',
        'x-jws-signature': 'DUMMY_SIG',
        'x-idempotency-key': '{}'.format(uuid.uuid4())
    }
    response = requests.request("POST", "{}/{}/funds-confirmation".format(VRP_consent_endpoint, consent_id),
                                headers=headers, data=payload)
    print(response.status_code)
    print("Funds Available Result:", response.json()['Data']['FundsAvailableResult']['FundsAvailable'])
    return response


# 6. Submit payment against VRP consent

def submit_payment(access_token, consent_id, amount):
    payload = json.dumps({
        "Data": {
            "ConsentId": "{}".format(consent_id),
            "PSUAuthenticationMethod": "UK.OBIE.SCANotRequired",
            "Initiation": {
                "CreditorAccount": {
                    "SchemeName": "SortCodeAccountNumber",
                    "Identification": "50499910000998",
                    "Name": "powered by PayPart",
                    "SecondaryIdentification": "secondary-identif"
                }
            },
            "Instruction": {
                "InstructionIdentification": "instr-identification",
                "EndToEndIdentification": "e2e-identification",
                "InstructedAmount": {
                    "Amount": "{}".format(amount),
                    "Currency": "GBP"
                },
                "CreditorAccount": {
                    "SchemeName": "SortCodeAccountNumber",
                    "Identification": "50499910000998",
                    "Name": "powered by PayPart",
                    "SecondaryIdentification": "secondary-identif"
                },
                "RemittanceInformation": {
                    "Unstructured": "Tools",
                    "Reference": "Tools"
                }
            }
        },
        "Risk": {}
    })
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'x-fapi-financial-id': '0015800000jfwxXAAQ',
        'Content-Type': 'application/json',
        'x-jws-signature': 'DUMMY_SIG',
        'x-idempotency-key': '{}'.format(uuid.uuid4())
    }

    response = requests.request("POST", payment_endpoint, headers=headers, data=payload)
    print(response.status_code)
    return response

# #making the calls
#
# # need to get access token for each payment
# access_token_call = get_access_token(scope="payments")
# access_token = access_token_call.json()['access_token'] ## access token that is passed through next function
# api_status = access_token_call.status_code ##this will give output 200 if successful
#
# ## need to get the VRP Consent for each payment
# consent_call = VRP_consent(amount_to_pay_per_user=30, access_token=access_token)
# consent_id = consent_call.json()['Data']['ConsentId']
# api_status = consent_call.status_code ##this will give output 201 if successful
#
#
# ## get customer authorisation, hard coded username until I can update the test data
# approve = get_consent(authorization="APPROVED", consent_id=consent_id, username="jpeterson@hackathon-team.2024.co.uk")
# redirecturi_response = approve.json()['redirectUri']
# get_code = re.search(r'code=([a-f0-9-]+)', redirecturi_response)
# consent_code = get_code.group(1)
# api_status = approve.status_code ##this will give output 200 if successful
#
# ## exchange authorisation code for access token
# exchange = exchange_code_for_token(code=consent_code)
# new_access_token = exchange.json()['access_token']
# api_status = exchange.status_code ##this will give output 200 if successful
#
# ## confirm account has the funds
# confirm_funds(access_token=new_access_token, consent_id=consent_id, amount=30)
#
# ## submit the payment
# submit_payment_request = submit_payment(access_token=new_access_token, consent_id=consent_id, amount=30)
# api_status = submit_payment_request.status_code ##this will be 201 if its successful
