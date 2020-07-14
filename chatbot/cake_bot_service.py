from io import BytesIO
from random import randint
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from chatbot.models import Customer, GiftCard
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


class DatabaseUpdater:

    def __init__(self, db_engine):
        self.session = Session(db_engine)

    def append_customer(self, user_data, platform='vk'):
        customers = self.session.query(Customer).all()
        print(user_data)
        params = user_data[0]

        username = params['first_name'] + ' ' + params['last_name']
        user_id = params['id']

        new_card = self.append_giftcard(user_id=user_id, username=username)

        if user_id not in [customer.user_id for customer in customers]:
            new_customer = Customer(name=username, user_id=user_id,
                                    platform=platform,
                                    timestamp_of_record=datetime.now(),
                                    card_number=new_card.card_number
                                    )
            self.session.add(new_customer)
        try:
            self.session.commit()
        except:
            self.session.rollback()

    def append_giftcard(self, user_id, username):
        card_number = int(str(user_id) + str(len(username)))
        GiftCardMaker().create_salescard(card_number)
        new_card = GiftCard(card_number=card_number, mechanics_id=1)
        self.session.add(new_card)

        try:
            self.session.commit()
        except:
            self.session.rollback()

        return new_card

    def get_giftcard_number(self, user_id):
        s = select([Customer.card_number]).where(Customer.user_id == user_id)
        result = self.session.execute(s).fetchone()
        return result[0]

    def check_user_id(self, user_id):
        s = select([Customer.user_id]).where(Customer.user_id == user_id)
        result = self.session.execute(s).fetchone()
        return True if result is not None and user_id == result[0] else False


class GiftCardMaker:
    """
    creating images (cards)
    :param path_to_template:
    :param path_to_font:
    :param text_color:
    :param saving_path:

    """

    def __init__(self, path_to_template='./external_data/images/templates/giftcard_template.png',
                 path_to_font='./external_data/images/fonts/Roboto-Bold.ttf',
                 text_color='rgb(135,220,163)',
                 saving_path='./external_data/images/giftcards/'):
        self.template = path_to_template
        self.font = ImageFont.truetype(path_to_font, size=100)
        self.text_color = text_color
        self.saving_path = saving_path

    def create_salescard(self, card_no):
        image = Image.open(self.template)
        draw = ImageDraw.Draw(image)
        (x, y) = (230, 530)
        sale_num = str(randint(5, 15)) + '%' if card_no != 0 else '10%'
        draw.text(xy=(x, y), text=sale_num, fill=self.text_color, font=self.font)
        del draw
        image.save(self.saving_path + 'salescard_' + str(card_no) + '.png')
        temp_file = BytesIO()
        image.save(temp_file, 'png')
        image.close()
        temp_file.seek(0)

        return temp_file


if __name__ == '__main__':
    GiftCardMaker().create_salescard(0)
