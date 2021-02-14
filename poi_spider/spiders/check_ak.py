from poi_spider.exc import (
    GeocoderAuthenticationFailure,
    GeocoderQueryError,
    GeocoderQuotaExceeded,
    GeocoderServiceError)

def check_bd_status(status_code):
    """
    Validates error statuses.
    """
    if status_code == 0:
        # When there are no results, just return.
        return True
    if status_code == 1:
        raise GeocoderServiceError(
            'Internal server error.'
        )
    elif status_code == 2:
        raise GeocoderQueryError(
            'Invalid request.'
        )
    elif status_code == 3:
        raise GeocoderAuthenticationFailure(
            'Authentication failure.'
        )
    elif status_code == 4:
        raise GeocoderQuotaExceeded(
            'Quota validate failure.'
        )
    elif status_code == 5:
        raise GeocoderQueryError(
            'AK Illegal or Not Exist.'
        )
    elif status_code == 101:
        raise GeocoderAuthenticationFailure(
            'No AK'
        )
    elif status_code == 102:
        raise GeocoderAuthenticationFailure(
            'MCODE Error'
        )
    elif status_code == 200:
        raise GeocoderAuthenticationFailure(
            'Invalid AK'
        )
    elif status_code == 211:
        raise GeocoderAuthenticationFailure(
            'Invalid SN'
        )
    elif 200 <= status_code < 300:
        raise GeocoderAuthenticationFailure(
            'Authentication Failure'
        )
    elif 300 <= status_code < 500:
        raise GeocoderQuotaExceeded(
            'Quota Error.'
        )
    else:
        raise GeocoderQueryError('Unknown error. status_code: %r' % status_code)



if __name__=="__main__":
    status_code=1
    # check_bd_status(status_code)
    raise 1