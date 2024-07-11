import os
from typing import Dict, Optional
import aiohttp
import xmltodict
from vocode.streaming.models.telephony import ExotelConfig
from vocode.streaming.telephony.client.abstract_telephony_client import AbstractTelephonyClient

class ExotelBadRequestException(ValueError):
    pass


class ExotelClient(AbstractTelephonyClient):
    def __init__(
        self,
        base_url,
        maybe_exotel_config: Optional[ExotelConfig] = None,
    ):
        
        self.exotel_config = maybe_exotel_config or ExotelConfig(
            account_sid=os.environ["EXOTEL_ACCOUNT_SID"],
            subdomain=os.environ["EXOTEL_ACCOUNT_SUBDOMAIN"],
            api_key=os.environ["EXOTEL_ACCOUNT_API_KEY"],
            api_token=os.environ["EXOTEL_ACCOUNT_API_TOKEN"],
            app_id=812068
        )

        super().__init__(base_url=base_url)
        

    def get_telephony_config(self):
        return self.exotel_config

    async def create_call(
        self,
        conversation_id: str,
        to_phone: str,
        from_phone: str,
        record: bool = False,
        digits: Optional[str] = None,
        telephony_params: Optional[Dict[str, str]] = None,
    ) -> str:
        data = {
            'From': to_phone,
            'CallerId': from_phone,
            **(telephony_params or {}),
            'Url': f'http://my.exotel.com/{self.exotel_config.account_sid}/exoml/start_voice/812068',
        }
        print(f'http://my.exotel.com/{self.exotel_config.account_sid}/exoml/start_voice/{self.exotel_config.app_id}')
        auth = aiohttp.BasicAuth(login=self.exotel_config.api_key, password=self.exotel_config.api_token)
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.post(f'https://{self.exotel_config.subdomain}/v1/Accounts/{self.exotel_config.account_sid}/Calls/connect',
                                    data=data) as response:
                if not response.ok:
                    raise RuntimeError(
                        f"Failed to start call: {response.status} {response.reason}"
                    )
                xml_data = await response.text()
                exotel_response = xmltodict.parse(xml_data)
                call_sid = exotel_response['TwilioResponse']['Call']['Sid']
            await session.close()
        return call_sid

    @staticmethod
    def create_call_exotel(base_url, conversation_id, is_outbound: bool = True, ):
        return {"url": f"wss://{base_url}/connect_call/{conversation_id}"}

    # TODO(EPD-186)
    def validate_outbound_call(
        self,
        to_phone: str,
        from_phone: str,
        mobile_only: bool = True,
    ):
        pass

    async def end_call(self, app_id):
        pass