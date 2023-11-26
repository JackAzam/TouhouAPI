import asyncio
from circle import Circle
from album import Album
from song import Songs

async def main():
    # Replace 'Example Circle' with the desired circle name
    circle_name = 'Foreground Eclipse'

    # Create an instance of the Circle class
    circle_instance = Circle()

    # Fetch circle details
    circle_details = await circle_instance._circle_details_by_name_or_id(circle_name)

    if 'error' in circle_details:
        print(f"Error fetching circle details: {circle_details['error']}")
        return

    print("Circle Details:", circle_details)

    # Create instances of Album and Songs
    album_instance = Album(circle_instance)
    songs_instance = Songs()

    # Fetch album details for the circle
    album_details = await album_instance.fetch_album_details(circle_name)

    if 'error' in album_details:
        print(f"Error fetching album details: {album_details['error']}")
    else:
        print("Album Details:", album_details)

        # Choose an album from the list (replace index with your choice)
        if 'items' in album_details:
            chosen_album = album_details['items'][0]
            album_id = chosen_album['id']

            # Fetch songs for the chosen album
            await songs_instance._songs_for_album(album_id)
            print("Songs:", songs_instance.song_list)
        else:
            print("No albums found for the specified circle.")

if __name__ == "__main__":
    asyncio.run(main())
