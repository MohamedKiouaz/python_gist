import openai
from pathlib import Path

def clean_movie_title(title):
    try:
        chat_completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"Please reformat the provided movie title into a clean and simplified version. The goal is to distill the title to its essential elements, typically the name of the movie and its year of release. Remove any extraneous details such as video resolution, encoding formats, release groups, or other technical specifications. Ensure that the final output retains the core identity of the movie, represented solely by its title and the year it was released. The focus should be on clarity and brevity, maintaining the essence of the movie's identity while discarding non-essential information. This is the title: '{title}'"
                }
            ],
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error processing title {title}: {e}")
        return title

# Example usage
main_path = Path("D:\Movies")
for movie_path in main_path.glob("**/*"):
    cleaned_title = clean_movie_title((movie_path.stem))
    cleaned_title.replace('"', '')

    movie_path.rename(main_path / f"{cleaned_title}{movie_path.suffix}")

    print(cleaned_title)
