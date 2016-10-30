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

    def test_laundry_stats(self):
        laundry_update()
        laundry_stats_update()

        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        room_names = json.loads(r.get("app.tasks.laundry.rooms"))

        for room in room_names:
            room_stats = json.loads(r.get("app.tasks.laundry.stats.{}".format(room)))

            room_stat = room_stats['room_stat']
            machine_stats = room_stats['machine_stats']
            self.assertIsInstance(room_stats["timestamp"], float)

            for hour in range(24):
                self.assertTrue(0 <= room_stat['total_open_by_hour'][hour])
                self.assertTrue(0 <= room_stat['total_usage_by_hour'][hour])
                self.assertTrue(0 <= room_stat['average_usage_by_hour'][hour] <= len(machine_stats))

            for machine_id in machine_stats:
                machine_stat = machine_stats[machine_id]

                self.assertTrue(0 <= machine_stat['total_powered'])
                self.assertTrue(0 <= machine_stat['total_usage'])
                self.assertTrue(0 <= machine_stat['daily_usage'] <= 86400)


if __name__ == '__main__':
    unittest.main()
