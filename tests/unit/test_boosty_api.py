from registration.adapters.boosty import BoostyAPI


def test_boosty_api_can_parse_subscribers_list():
    response = subscribers_list_response_sample.encode("utf-8")
    profiles = BoostyAPI.parse_subscriber_list_data(response)

    assert len(profiles) == 3
    assert profiles[0].name == "Alex Shivilov"
    assert profiles[0].level.name == "Хуевый оберег"
    assert profiles[1].name == "Vit'ka"
    assert profiles[1].level.name == "Хуевый оберег"
    assert profiles[2].name == "Rina Erxori"
    assert profiles[2].level.name == "Хуевый оберег"


subscribers_list_response_sample = """{
    "total": 3,
    "limit": 11,
    "offset": 3,
    "data": [
        {
            "hasAvatar": true,
            "price": 200,
            "avatarUrl": "https://images.boosty.to/user/23288255/avatar?change_time=1696788941",
            "payments": 909,
            "canWrite": true,
            "nextPayTime": 1710526823,
            "email": "alex.shivilov04@gmail.com",
            "isBlackListed": false,
            "name": "Alex Shivilov",
            "level": {
                "ownerId": 23282104,
                "id": 2165598,
                "isArchived": false,
                "currencyPrices": {
                    "RUB": 200,
                    "USD": 2.24
                },
                "data": [
                    {
                        "width": 1280,
                        "type": "image",
                        "height": 720,
                        "id": "0ede1540-1612-4252-b157-d8aa26d9c695",
                        "rendition": "",
                        "url": "https://images.boosty.to/image/0ede1540-1612-4252-b157-d8aa26d9c695?change_time=1696788744"
                    },
                    {
                        "type": "text",
                        "content": "",
                        "modificator": ""
                    },
                    {
                        "modificator": "BLOCK_END",
                        "content": "",
                        "type": "text"
                    },
                    {
                        "type": "text",
                        "content": "",
                        "modificator": ""
                    },
                    {
                        "type": "text",
                        "content": "",
                        "modificator": "BLOCK_END"
                    }
                ],
                "createdAt": 1696788742,
                "deleted": false,
                "price": 200,
                "name": "Хуевый оберег"
            },
            "onTime": 1705342823,
            "id": 23288255,
            "subscribed": true
        },
        {
            "email": "vgutiyeva@bk.ru",
            "nextPayTime": 1709835444,
            "name": "Vit'ka",
            "isBlackListed": false,
            "id": 23296407,
            "onTime": 1699467444,
            "level": {
                "currencyPrices": {
                    "USD": 2.24,
                    "RUB": 200
                },
                "data": [
                    {
                        "rendition": "",
                        "url": "https://images.boosty.to/image/0ede1540-1612-4252-b157-d8aa26d9c695?change_time=1696788744",
                        "id": "0ede1540-1612-4252-b157-d8aa26d9c695",
                        "width": 1280,
                        "type": "image",
                        "height": 720
                    },
                    {
                        "modificator": "",
                        "type": "text",
                        "content": ""
                    },
                    {
                        "content": "",
                        "type": "text",
                        "modificator": "BLOCK_END"
                    },
                    {
                        "type": "text",
                        "content": "",
                        "modificator": ""
                    },
                    {
                        "modificator": "BLOCK_END",
                        "content": "",
                        "type": "text"
                    }
                ],
                "isArchived": false,
                "ownerId": 23282104,
                "id": 2165598,
                "deleted": false,
                "price": 200,
                "name": "Хуевый оберег",
                "createdAt": 1696788742
            },
            "subscribed": true,
            "hasAvatar": true,
            "price": 200,
            "payments": 900,
            "avatarUrl": "https://images.boosty.to/user/23296407/avatar?change_time=1697042177",
            "canWrite": true
        },
        {
            "hasAvatar": true,
            "price": 200,
            "avatarUrl": "https://images.boosty.to/user/18082736/avatar?change_time=1683201487",
            "payments": 900,
            "canWrite": true,
            "nextPayTime": 1709976466,
            "email": "rerxori@gmail.com",
            "isBlackListed": false,
            "name": "Rina Erxori",
            "onTime": 1697016466,
            "level": {
                "currencyPrices": {
                    "RUB": 200,
                    "USD": 2.24
                },
                "data": [
                    {
                        "height": 720,
                        "width": 1280,
                        "type": "image",
                        "url": "https://images.boosty.to/image/0ede1540-1612-4252-b157-d8aa26d9c695?change_time=1696788744",
                        "rendition": "",
                        "id": "0ede1540-1612-4252-b157-d8aa26d9c695"
                    },
                    {
                        "type": "text",
                        "content": "",
                        "modificator": ""
                    },
                    {
                        "modificator": "BLOCK_END",
                        "type": "text",
                        "content": ""
                    },
                    {
                        "type": "text",
                        "content": "",
                        "modificator": ""
                    },
                    {
                        "type": "text",
                        "content": "",
                        "modificator": "BLOCK_END"
                    }
                ],
                "isArchived": false,
                "ownerId": 23282104,
                "id": 2165598,
                "deleted": false,
                "price": 200,
                "name": "Хуевый оберег",
                "createdAt": 1696788742
            },
            "id": 18082736,
            "subscribed": true
        }
    ]
}"""
