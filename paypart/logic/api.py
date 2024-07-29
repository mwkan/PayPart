import requests
import json
import uuid
import re

# endpoints
issuer = "https://api.sandbox.natwest.com"
authorization_endpoint = "https://api.sandbox.natwest.com/authorize"
token_endpoint = "https://ob.sandbox.natwest.com/token"
VPR_consent_endpoint = "https://ob.sandbox.natwest.com/open-banking/v3.1/pisp/domestic-vrp-consents"
jwks_uri = "https://keystore.openbankingtest.org.uk/0015800000jfwxXAAQ/0015800000jfwxXAAQ.jwks"
registration_endpoint = "https://ob.sandbox.natwest.com/register"
payment_endpoint = "https://ob.sandbox.natwest.com/open-banking/v3.1/pisp/domestic-vrps"

# environment variables
client_id = "QdWMOwmqVtVXZlFAD_mI5CyRdGQD4J58BYduuIkxZzg%3D"
client_secret = "__yi_l6ny7Nsa7GjM32e3baiIghwdAG_CoRKRhPTH-s%3D"
idempotency_key = uuid.uuid4()

# 1. get access token

def get_access_token(scope):
    payload = 'grant_type=client_credentials&client_id={}&client_secret={}&scope={}'.format(client_id, client_secret, scope)
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", token_endpoint, headers=headers, data=payload)
    print("get_access_token call status:", response.status_code)
    print("access_token:", response.json()['access_token'])
    return response

# 2. create a VPR consent

def VPR_consent(amount_to_pay_per_user, access_token):
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
      'x-idempotency-key': '{}'.format(idempotency_key)
    }

    response = requests.request("POST", VPR_consent_endpoint, headers=headers, data=payload)

    print("VRP call status:", response.status_code)
    print("consent_id:", response.json()['Data']['ConsentId'])
    return response


# 3. redirect customer to approve a VRP consent
# need to add in step here to get account information
def get_consent(authorization, consent_id, username):

    account_number = "50000011223301"

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
    #print(response.text)
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
    payload = json.dumps(
        {
            "Data": {
                "ConsentId": "{}".format(consent_id),
                "Reference": "PayPart payment",
                "InstructedAmount": {
                    "Amount": "{}".format(amount),
                    "Currency": "GBP"
                }
            },
            "Risk": {}
        }
    )
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "x- fapi-financial-id": "0015800000jfwxXAAQ",
        "x-fapi-auth-date" : "Sun, 16 Sep 2018 11: 43:31 UTC",
        "x-fapi-customer-ip-address": "1.2.3.4",
        "x-fapi-interaction-id": "{}".format(uuid.uuid4()),
        "Content-Type" : "application/json",
        "Accept": "application/json",
        'x-idempotency-key': '{}'.format(idempotency_key),
        'x-jws-signature': 'DUMMY_SIG',
    }
    response = requests.request("POST", VPR_consent_endpoint, headers=headers, data=payload)
    print(response.text)
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
      'x-idempotency-key': '{}'.format(idempotency_key)
    }

    response = requests.request("POST", payment_endpoint, headers=headers, data=payload)

    print(response.text)





#making the calls

## need to get access token for each payment
access_token_call = get_access_token(scope="payments")
access_token = access_token_call.json()['access_token'] ## access token that is passed through next function
api_status = access_token_call.status_code ##this will give output 200 if successful

## need to get the VRP Consent for each payment
consent_call = VPR_consent(amount_to_pay_per_user=30, access_token=access_token)
consent_id = consent_call.json()['Data']['ConsentId']
api_status = consent_call.status_code ##this will give output 201 if successful


## get customer authorisation, hard coded username until I can update the test data
approve = get_consent(authorization="APPROVED", consent_id=consent_id, username="djefferson@hackathon-team.2024.co.uk")
redirecturi_response = approve.json()['redirectUri']
get_code = re.search(r'code=([a-f0-9-]+)', redirecturi_response)
consent_code = get_code.group(1)
api_status = approve.status_code ##this will give output 200 if successful

## exchange authorisation code for access token
exchange = exchange_code_for_token(code=consent_code)
new_access_token = exchange.json()['access_token']
api_status = exchange.status_code ##this will give output 200 if successful

## submit the payment
submit_payment(access_token=new_access_token, consent_id=consent_code, amount=30)




