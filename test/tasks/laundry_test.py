import unittest
from tasks.laundry import *


class TestLaundry(unittest.TestCase):
    def test_laundry_update(self):
        laundry_update()

        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        raw_data = json.loads(r.get("app.tasks.laundry"))
        room_names = json.loads(r.get("app.tasks.laundry.rooms"))

        for room in room_names:
            room_data = json.loads(r.get(room))
            self.assertIsInstance(room_data["id"], basestring)
            self.assertIsInstance(room_data["machine"], list)
            self.assertIsInstance(room_data["networked"], basestring)
            self.assertIsInstance(room_data["timestamp"], float)


if __name__ == '__main__':
    unittest.main()
