import json
import redis
import numpy as np
import matplotlib.pyplot as plt


def draw(room_names):
    bar_width = 0.8
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    for room in room_names:
        room_stats = json.loads(r.get("app.tasks.laundry.stats.{}".format(room)))

        plt.figure()
        plt.title('Room Statistics By Hour for {}'.format(room))
        hours = np.arange(24)
        plt.bar(hours, room_stats['room_stat']['average_usage_by_hour'], bar_width)
        plt.xticks(hours + bar_width / 2, hours)

        plt.figure()
        plt.title('Room Statistics By Weekday for {}'.format(room))
        days = np.arange(7)
        plt.bar(days, room_stats['room_stat']['average_usage_by_day'], bar_width)
        plt.xticks(days + bar_width / 2, days + 1)

        plt.figure()
        plt.title('Machine Statistics for {}'.format(room))
        machine_stats = room_stats['machine_stats']
        daily_usages = [machine_stats[machine_id]['daily_usage'] for machine_id in machine_stats]
        machines = np.arange(len(daily_usages))
        plt.bar(machines, daily_usages, bar_width)
        plt.xticks(machines + bar_width / 2, machine_stats.keys())

    plt.show()

if __name__ == '__main__':
    draw(['ISR: Wardall'])
