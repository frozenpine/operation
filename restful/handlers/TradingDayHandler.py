# -*- coding: UTF-8 -*-
from app import db
from sqlalchemy import text
import arrow
from flask_restful import Resource

class NextTradingDayApi(Resource):
    def get(self):
        next_trading_day = db.session.execute(
            text(
                "\
                SELECT trade_calendar.full_date \
                FROM trade_calendar \
                WHERE trade_calendar.full_date>'{}' \
                    AND trade_calendar.is_trade=1 \
                LIMIT 1\
                ".format(arrow.utcnow().to('Asia/Shanghai').format('YYYYMMDD'))
            )
        ).first()[0]
        return next_trading_day
