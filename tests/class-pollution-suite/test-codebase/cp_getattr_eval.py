def getattr_through_eval(obj, attrs, val):
    """
    @name: getattr_through_eval
    @category: class-pollution-func
    @type: get-eval+set-attr
    @desc: Check if the taint propagates through eval-based attribute access.
    @result: getattr_through_eval should be marked as vulnerable.
    """
    access_expr = 'obj'
    for attr in attrs[:-1]:
        access_expr += f'.{attr}'
    target = eval(access_expr)
    setattr(target, attrs[-1], val)