# -*- coding: UTF-8 -*-
import arrow
from flask import current_app
from flask_restful import Resource
from sqlalchemy import text

from app import db


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
                ".format(arrow.utcnow().to(current_app.config['TIME_ZONE']).format('YYYYMMDD'))
            )
        ).first()[0]
        return next_trading_day


class CurrentTradingDayApi(Resource):
    pass
