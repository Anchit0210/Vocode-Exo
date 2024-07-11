import os

from dotenv import load_dotenv

from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.telephony import ExotelConfig

load_dotenv()

from speller_agent import SpellerAgentConfig

from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.conversation.outbound_call import OutboundCall

from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig

BASE_URL = os.environ["BASE_URL"]

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("YOUR_VOICE_ID")


# Configure ElevenLabs synthesizer
synthesizer_config = ElevenLabsSynthesizerConfig.from_telephone_output_device(
    api_key=api_key,
    voice_id=voice_id
)

def get_assistant_instructions():
  # Open the file and read its contents
  with open(r'E:\LiaPlus\Vocode-python\VOCODE-CORE\Exotel Implementing vocode\vocode-core-main\apps\telephony_app\instructions.txt', 'r') as file:
    return file.read()

async def main():
    config_manager = RedisConfigManager()

    outbound_call = OutboundCall(
        base_url=BASE_URL,
        to_phone="",
        from_phone="",
        synthesizer_config=synthesizer_config,
        config_manager=config_manager,
        agent_config=ChatGPTAgentConfig(
            initial_message=BaseMessage(text="Hello"),
            prompt_preamble="Have a pleasant conversation about life",
            generate_responses=True,
        ),
        telephony_config=ExotelConfig(
            account_sid=os.environ["EXOTEL_ACCOUNT_SID"],
            subdomain=os.environ["EXOTEL_ACCOUNT_SUBDOMAIN"],
            api_key=os.environ["EXOTEL_ACCOUNT_API_KEY"],
            api_token=os.environ["EXOTEL_ACCOUNT_API_TOKEN"],
        ),
    )

    input("Press enter to start call...")
    await outbound_call.start()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())