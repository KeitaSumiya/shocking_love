# preparation 1
- get lots of images for people
- get lots of images for yourself (in my case, it's about photos for me)

# preparation 2(trim faces in images)
> [your dir]/shocking_love/python/preparation/trims_dlib/main.py

```
Directory setting in [your dir]/shocking_love/python/preparation/trims_dlib/
- main.py
- in/img1.jpg
- in/img2.jpg
...
...
...
- out/
```

```
cd [your dir]/shocking_love/python/preparation/trims_dlib
python main.py
```

```
results: 
- out/img1_0-1.jpg
- out/img2_1-1.jpg
...
...
...
```

# preparation 3(deep learning by tensorflow)
> [your dir]/shocking_love/python/preparation/tf/learn.py

```
Directory setting in [your dir]/shocking_love/python/preparation/tf/
- data/
- learn.py
- test/img1.jpg
- test/img2.jpg
...
...
...
- train/img1_0-1.jpg
- train/img2_1-1.jpg
...
...
...
```

```
cd [your dir]/shocking_love/python/preparation/
python learn.py
```
In this step, you can get learned model file "model.ckpt". 

```
results: 
...
...
- data/
- learn.py
- model.ckpt
...
...
...
```


# preparation 4(check your training result and predict labels for another new images by tensorflow)
> [your dir]/shocking_love/python/preparation/tf/check.py

```
Directory setting in [your dir]/shocking_love/python/preparation/tf/
- check.py
- in/img1.jpg
- in/img2.jpg
...
...
...
```

```
cd [your dir]/shocking_love/python/preparation/
python check.py
```

# SHOKING LOVE
> [your dir]/shocking_love/python/main.py

```
Directory setting in [your dir]/shocking_love/python/  
- main.py
- in/model.ckpt
- in/heart60.wav
- in/heart120.wav
```

and, do the following command:

```
python main.py
```

THAT'S IT!!

