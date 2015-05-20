from .ultility import NotImplementFeatureException, UnsupportFeatureException

def test_not_implement_feature_exception():
    try:
        raise NotImplementFeatureException("some")
    except NotImplementFeatureException as e:
        assert e.message == 'some'
    try :
        raise NotImplementFeatureException(feature="some")
    except NotImplementFeatureException as e:
        assert e.message == '%s is not implemented' % 'some'

def test_unsupport_feature_exception():
    try :
        raise UnsupportFeatureException("some")
    except UnsupportFeatureException as e:
        assert e.message == 'some'
    try :
        raise UnsupportFeatureException(feature="some")
    except UnsupportFeatureException as e:
        assert e.message == '%s is unsupport' % 'some'

