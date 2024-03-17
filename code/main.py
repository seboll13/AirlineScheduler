from routes import Routes


if __name__ == "__main__":
    hub, dst = "LSGG", "OMDB"
    route = Routes(hub, dst)
    print(f'Distance {hub} to {dst}: {route.distance:.2f} km')
