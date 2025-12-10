#used to execute respective function based on user query
import task1
from config import key
import requests #web

def parse_function_response(message):
	function_call=message[0].get("functionCall")
	function_name=function_call["name"]
	print("Gemini : call function ",function_name)
	try:
		arguments = function_call.get("args")
		print("Gemini: arguments are ",arguments)
		if arguments:
			d=getattr(task1,function_name)
			print ("function is ",d)
			function_response=d(**arguments)
		else:
			function_response="No arguments are present"

	except Exception as e:
		print(e)	
		function_response="Invalid Function"
	return function_response

def run_conversation(user_message):
	messages = [] #list of all messages
	print(user_message)

	system_message = """You are an AI bot that can do everything using function call. 
	When you are asked to do something, use the function call you have available
	and then respond with message""" # first instruction

	message = { "role":"user",
				"parts":[{"text":system_message+"\n"+user_message}] }

	messages.append(message)

	data = {"contents":[messages],
			"tools":
			[ {"functionDeclarations": task1.definitions
			  }]
			}
	url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key="+key
	response = requests.post(url,json=data)

	if response.status_code!=200:
		# Log full response for debugging and return a user-friendly message
		print("Non-200 response from API:", response.status_code, response.text)
		return "Sorry, I couldn't get a response from the model (non-200 status)."

	try:
		t1 = response.json()
	except ValueError:
		print("Failed to parse JSON from response:", response.text)
		return "Sorry, I couldn't parse the model response."

	# Validate structure before indexing
	candidates = t1.get("candidates")
	if not candidates or not isinstance(candidates, list):
		print("Error: No candidates in response:", t1)
		return "Sorry, I couldn't get a response from the model (no candidates)."

	candidate = candidates[0]
	if not isinstance(candidate, dict):
		print("Error: Candidate is not an object:", candidate)
		return "Sorry, I received an unexpected response format from the model."

	content = candidate.get("content")
	if not content or not isinstance(content, dict):
		print("Error: No content in candidate:", candidate)
		return "Sorry, model response did not include content."

	parts = content.get("parts")
	if not parts or not isinstance(parts, list):
		print("Error: No parts in content:", content)
		return "Sorry, model content is missing parts."

	print("Message #######:", parts)

	# Handle function call responses
	first_part = parts[0]
	if isinstance(first_part, dict) and 'functionCall' in first_part:
		try:
			resp1 = parse_function_response(parts)
			print("Actual response", resp1)
			return resp1
		except Exception as e:
			print("Error while handling functionCall:", e)
			return "Sorry, there was an error executing the requested function."

	# Handle normal text responses: parts may be dicts with 'text' or plain strings
	if isinstance(first_part, dict) and 'text' in first_part:
		return first_part.get('text', '')

	if isinstance(first_part, str):
		return first_part

	# Fallback: return a stringified version of parts
	return str(parts)


if __name__=="__main__":
	user_message = "find the ip address of google.com"

	print (run_conversation(user_message))
