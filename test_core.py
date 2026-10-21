import pytest
from daily_ease.db import init_db, get_session, User, WorkerProfile
from daily_ease.auth import register_user, authenticate, verify_password, hash_password
from daily_ease.services import search_workers, create_request, list_requests, change_request_status, update_worker_profile
from daily_ease.i18n import TRANSLATIONS, missing_keys

@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    init_db(f"sqlite:///{tmp_path / 'test.db'}")
    yield

def add_worker(email="worker@example.com"):
    uid=register_user("Worker One",email,"strong-password-1","Gorakhpur","worker")
    update_worker_profile(uid,"Electrician","Wiring, fan repair","Helpful local worker",3,"₹300 onwards","Weekdays","Hindi")
    return uid

def test_password_hashing_and_login():
    uid=register_user("Test Customer","c@example.com","strong-password-1","Gorakhpur")
    with get_session() as s:
        u=s.get(User,uid); assert u.password_hash != "strong-password-1"; assert verify_password("strong-password-1",u.password_hash)
    assert authenticate("c@example.com","strong-password-1")["id"]==uid
    assert authenticate("c@example.com","wrong-password") is None

def test_duplicate_account_rejected():
    register_user("Test Customer","c@example.com","strong-password-1","Gorakhpur")
    with pytest.raises(ValueError): register_user("Other Customer","C@example.com","strong-password-1","Gorakhpur")

def test_search_and_category_filter():
    add_worker(); assert len(search_workers("wiring","Electrician","Gorakhpur"))==1
    assert search_workers("wiring","Plumber")==[]

def test_request_flow_and_permissions():
    customer=register_user("Customer One","c@example.com","strong-password-1","Gorakhpur")
    worker=add_worker()
    rid=create_request(customer,worker,"Repair a ceiling fan","Gorakhpur","Tomorrow morning")
    assert list_requests(customer,"customer")[0]["id"]==rid
    with pytest.raises(PermissionError): change_request_status(rid,customer,"customer","Accepted")
    change_request_status(rid,worker,"worker","Accepted")
    change_request_status(rid,worker,"worker","In Progress")
    change_request_status(rid,worker,"worker","Completed")
    assert list_requests(customer,"customer")[0]["status"]=="Completed"

def test_customer_cannot_create_request_as_worker():
    c=register_user("Customer One","c@example.com","strong-password-1","Gorakhpur")
    w=add_worker()
    with pytest.raises(PermissionError): create_request(w,c,"Need a repair","Gorakhpur")

def test_translations_have_no_missing_keys():
    assert all(not missing for missing in missing_keys().values())
    assert {"en","hi","hinglish"} <= set(TRANSLATIONS)

def test_worker_profile_update_authorization():
    c=register_user("Customer One","c@example.com","strong-password-1","Gorakhpur")
    with pytest.raises(PermissionError): update_worker_profile(c,"Tutor","Maths","",0,"","","Hindi")
