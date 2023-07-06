import datetime


def date_has_expired(date):
    """[Compare Today and Expiry Date]

    Args:
        date ([date]): [Expiry date of Coupon]

    Returns:
        [bool]: [Returns True or False]
    """    
    return date < datetime.date.today()


def check_coupon(coupon, plan_price):
    """
    [Coupon Validation and Discount Apply]

    Args:
        coupon ([object]): [All data of object]
        plan_price ([int]): [value of plan price]

    Returns:
       final_amount [int]: [final_amount]
    """    
    coupon_use_limit = coupon.use_limit or 0
    use_limit_remaining = (coupon_use_limit - coupon.coupon_used)
    code_expiry = coupon.expiry_date
    '''
    print('========Coupon========')
    print('Coupon Found = ', coupon)
    print('Coupon Type = ', coupon.discount_type)
    print('Coupon Use Remaining = ', use_limit_remaining)
    print('Coupon Expiry Date = ', code_expiry)
    print("has_expired = ", date_has_expired(code_expiry))
    print('========Coupon========')
    '''
    # Check the coupon Status
    if not coupon.status:
        return 'not_activated'

    # Check Coupon Expiry Date
    if date_has_expired(code_expiry):
        # return Response({'message': 'Coupon has been expired'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return 'code_expired'

    # Check Coupon Use Limit
    if coupon.use_limit and use_limit_remaining <= 0:
        # return Response({'message': 'Coupon limit exceeded'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return 'limit_exceeded'

    # Check if Discount in Percentage or in Amount
    if coupon.discount_type != 'percent':
        # print('Discount Calc for Amount')
        return plan_price - int(coupon.discount)

    # print('Discount Calc for Percentage')
    discount = (plan_price * int(coupon.discount)/100)
    return plan_price - discount


# Get Months to Expiry Date

def get_expiry_date(validity):
    """[Months to Expiry Date Calculation]
    * for now we are taking 30.41 days in every months for makeup year's 365 days.
    Args:
        validity ([int]): [ Pass Validity in Months ]
        ex. if validity 6 then calculate from today to after 6 months.

    Returns:
        [date]: [ Expiry Date of Plan ]
    """    
    return datetime.date.today() + datetime.timedelta(days=round(int(validity) * 30.41))