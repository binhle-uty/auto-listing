from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from typing import Dict, List
import os
GROQ_API_KEY="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"

class AILising:
    '''
    This class is used to get response from Groq API
    '''
    def __init__(self) -> None:
        # Initialize API KEY
        self.GROQ_API_KEY = GROQ_API_KEY

    def load_model(self):
        "Load the model from the Langchain-Groq"
        self.chat = ChatGroq(temperature=0,
                             groq_api_key=self.GROQ_API_KEY, 
                             model_name="llama3-8b-8192")

    def get_prompt(self, 
                    product_name: str,
                    pack: str,
                    organic_keys: List[str], 
                    auto_keys: List[str],
                    customers: List[str],):
        "Build the prompt template"

        system = "You are doing the role of a Amazon Product Listing expert"
        human = f"""
                    Giving a product with {product_name} together with information of pack or size as {pack},
                    and with some ORGANIC IMPORTANT KEYS: {organic_keys} which need to be listed,
                    and reference keys: {auto_keys} which can be used to improve the listing performance.

                    Write a whole LISTING product for me to sale in Amazon US. 

                    The listing MUST push the brand "AMAZIN CHOICES" in the first place in title, to make the branding.
                    The information of pack and product size should be at the end of the title.

                    All infomation of KEYS listing should be covered.

                    There are rules you MUST follow:
                    - Title does not contain symbols or emojis
                    - Title contains around 150 characters
                    - Description has greater than 5 and less than 10 bullet points
                    - Description has greater than 150 characters in each bullet point
                    - MUST USE the icons, emojis, and symbols at the begin of each bullet point.
                    - First letter of bullet points is capitalized
                    - Bullet points are not in all caps or contain icons
                    - 1000+ characters in description or A+ content
                    - NOT using words or term phrase which I need to make verify. Example: Guaranteed, Approved, Verified, ...
                    

                    The response in format:

                    ## Title: 
                    Appropriate title of product using best keyword list, format as a header
                    ## Description: 
                        - description of the product, in bullet points, contains best keyword list to increase highest possibility of keyword search in amazon
                        - description MUST adapt style of sentenses to target to the group of customers on amazon: {customers}.
                    The return will be on MARKDOWN format.
                    

                    ALL OF THE NOTE NEED TO BE SKIPPED
                """
        self.prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    def get_response(self, 
                     product_name: str,
                     pack: str,
                     organic_keys: List[str], 
                     auto_keys: List[str],
                     customers: List[str],
                     ) -> List[Dict]:
        "Get the response from Groq API"
        self.load_model()
        self.get_prompt(product_name=product_name, 
                        pack = pack,
                        organic_keys=organic_keys, 
                        auto_keys = auto_keys,
                        customers=customers)
        self.chain = self.prompt | self.chat
        self.result = self.chain.invoke({"product_name": product_name,
                                         "pack": pack,
                                        "organic_keys": organic_keys,
                                        "auto_keys": auto_keys,
                                        "customers": customers,
                                        })
        return self.result
    

if __name__ == '__main__':
    PRODUCT = 'Coconut Milk Tea' 
    AUTO_KEYWORDS = ['', 'fresh', 'no added sugar']
    CUSTOMERS=['young kids', 'gym members']
    PACK = "16.9 oz (Pack of 1)"
    ORGANIC_KEYS = ['Vietnamese', 'fresh', 'no added sugar']

    ai_system = AILising()
    result = ai_system.get_response(product_name=PRODUCT,
                                    pack=PACK,
                                    organic_keys=ORGANIC_KEYS,
                                    auto_keys = AUTO_KEYWORDS,
                                    customers=CUSTOMERS,
                                    )
    content = (result.content)

    title = content.split("## Title:")[1].split("## Description:")[0].strip()
    description = content.split("## Description:")[1].strip()

    print(title)
    print(description)
