def test_404_for_unknown_path(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_500_for_problem_service(client):
    @client.application.route("/test-500")
    def trigger_500():
        raise Exception("Test exception for 500 error")

    response = client.get("/test-500")
    assert response.status_code == 500
    assert b"Sorry, there is a problem with the service" in response.data
