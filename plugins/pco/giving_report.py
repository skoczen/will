import pypco
import os
import datetime
import parsedatetime
import datetime
from datetime import date
import re
from will import settings
from plugins.pco.msg_attachment import SlackAttachment

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])
attachment_list = []

today = datetime.datetime.today().strftime('%Y-%m-%d')


# print("Today: %s" % today)


def get_giving(report_date="Last Monday"):
    fund_totals = {}
    online_giving = 0
    total_giving = 0
    fee_total = 0
    cal = parsedatetime.Calendar()
    report_date, parse_status = cal.parse(report_date)
    if parse_status:
        report_date = datetime.datetime(*report_date[:6])
        report_date = report_date.strftime('%Y-%m-%d')
    msg = "Giving: %s - %s" % (report_date, datetime.date.today()) + "\n"
    for donation in pco.giving.donations.list(where={"[created_at][gte]": report_date},
                                              include={'designations, labels'}):
        for label in donation.rel.labels.list():
            print(label.attributes['slug'])
        if donation.payment_method == 'ach' or donation.payment_method == 'card':
            online_giving += donation.amount_cents

        fee_total += donation.fee_cents

        for d in donation.rel.designations.list():
            if d.relationships['fund']['data']['id'] in fund_totals:
                fund_totals[d.relationships['fund']['data']['id']] += d.amount_cents
            else:
                fund_totals[d.relationships['fund']['data']['id']] = d.amount_cents

    # print("Online Giving: %s" % '{0:.2f}'.format(online_giving / 100))
    for fund, amount in fund_totals.items():
        total_giving += amount
        msg += ": $".join([pco.giving.funds.get(fund).name, '{:,.2f}'.format(amount / 100)]) + "\n"
    total_giving += fee_total
    if online_giving:
        msg += "\n".join(["Online Giving: %s%%" % '{:,.2f}'.format(online_giving / total_giving * 100),
                          "Fees: $%s" % '{:,.2f}'.format(fee_total / 100),
                          "---------------\nTotal: $%s" % '{:,.2f}'.format(total_giving / 100)])
    else:
        msg += "---------------\nTotal: $%s" % '{:,.2f}'.format(total_giving / 100)
    attachment = SlackAttachment(msg, pco='giving', text=msg, button_url="https://giving.planningcenteronline.com/"
                                                                         "donations?within=%s..%s" % (report_date,
                                                                                                      date.today()))
    attachment_list.append(attachment)
    return attachment_list


if __name__ == '__main__':
    x = get_giving()
    for attachment in x:
        print(attachment.slack())