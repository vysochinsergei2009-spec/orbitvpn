from aiocryptopay import AioCryptoPay, Networks
import asyncio

crypto = AioCryptoPay(token='468179:AAZNe5s3RXaHvdXzVYSbSAbgbbs2XVr1eh9', network=Networks.MAIN_NET)

async def main():
    profile =  await crypto.get_me()
    currencies =  await crypto.get_currencies()
    rates =  await crypto.get_exchange_rates()

    print(rates)

if __name__ == "__main__":
    asyncio.run(main())