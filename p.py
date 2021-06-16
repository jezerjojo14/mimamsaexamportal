VOWELS=['a', 'e', 'i', 'o', 'u', 'y', 'A', 'E', 'I', 'O', 'U', 'Y']

s="""
There's one hundred and four days of summer vacation
And school comes along just to end it
So the annual problem for our generation
Is finding a good way to spend it

Like maybe...
Building a rocket
Or fighting a mummy
Or climbing up the Eiffel Tower

Discovering something that doesn't exist (Hey! )
Or giving a monkey a shower

Surfing tidal waves
Creating nanobots
Or locating Frankenstein's brain (It's over here! )

Finding a dodo bird
Painting a continent
Or driving your sister insane (Phineas! )

As you can see
There's a whole lot of stuff to do
Before school starts this fall (Come on Perry)

So stick with us 'cause Phineas and Ferb
Are gonna do it all
So stick with us 'cause Phineas and Ferb are
Gonna do it all!
(Mom! Phineas and Ferb are making a title sequence! )
(Guitar downs)

"""
new_s=""
lines=s.splitlines()

for line in lines:
    words=line.split()

    for word in words:
        b=True
        while b:
            if len(word):
                if word[0].isalpha():
                    if word[0] in VOWELS:
                        b=False
                        if word[0].isupper():
                            new_s+="P"+word.lower()+" "
                        else:
                            new_s+="p"+word+" "
                else:
                    new_s+=word[0]
            else:
                b=False
            word=word[1:]
    new_s+='\n'

print(new_s)
