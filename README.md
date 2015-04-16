Evolutionary Grammar Generator
================


Instructions (tested on OS X and Python 2.7):

1. `python evolve.py first 100` to generate your initial population of grammars (pass count)
2. (Optional) `python evolve.py mutate gen` to mutate your genotypes (pass the relative directory where the `.json` files reside)
2. Inside of [Structure Synth](http://structuresynth.sourceforge.net/) open the `build.es` file you just generated and hit the build button
2. (Optional) `python custom_junk_images.py c gen/gen` to add junk images to your images directory
3. Two options:
    1. Place the images that rank highly with regards to your fitness function (preferences) inside of the `wow` sub-directory
    2. Use Mechanicl Turk:
        1. `python mechcnical_turk.py g gen/gen` to generate the html for mechanical turk
        2. `python mechcnical_turk.py p <directory_to_obtain_images> <experiment_num>` ex: `python mechcnical_turk.py p gen/gen 1` to generate analysis and put files in the `wow` directory
5. `python evolve.py crossover gen/wow` to generate offspring (pass the relative directory name where your chosen `.png` files reside) 
6. Repeat steps 2-5 as many times as you would like, continually adding sub-directories to your parameters

Here is some example output from Structure Synth using this GrammarGenerator:

![100-A-D-6-5-2-3.png](favorites/100-A-D-6-5-2-3.png)
![108-3-4-5-A-A-6-F-C-7-6.png](favorites/108-3-4-5-A-A-6-F-C-7-6.png)
![108-4-A-6-C-7-6.png](favorites/108-4-A-6-C-7-6.png)
![132-C-A-6-C-7-6.png](favorites/132-C-A-6-C-7-6.png)
![15-6-D-B-F-F-2.png](favorites/15-6-D-B-F-F-2.png)
![164-A-1-7-0-5-5-5-5-C.png](favorites/164-A-1-7-0-5-5-5-5-C.png)
![167-6-D-B-F-F-2.png](favorites/167-6-D-B-F-F-2.png)
![194-5-9-6-3-5-6-F-7-7-F.png](favorites/194-5-9-6-3-5-6-F-7-7-F.png)
![197-1-D-3-5-6-F-7-F.png](favorites/197-1-D-3-5-6-F-7-F.png)
![199-D-0-5-5-5-C.png](favorites/199-D-0-5-5-5-C.png)
![222-B-D-6-5-2-3.png](favorites/222-B-D-6-5-2-3.png)
![225-B-A-6-C-7-6.png](favorites/225-B-A-6-C-7-6.png)
![229-F-A-D-B-F-F-2.png](favorites/229-F-A-D-B-F-F-2.png)
![232-2-2-D-B-F-F-C-2.png](favorites/232-2-2-D-B-F-F-C-2.png)
![233-3-7-0-5-5-5-2-5-C.png](favorites/233-3-7-0-5-5-5-2-5-C.png)
![234-1-3-5-6-7-F-F.png](favorites/234-1-3-5-6-7-F-F.png)
![235-9-0-C-0-5-5-5-C-5-C.png](favorites/235-9-0-C-0-5-5-5-C-5-C.png)
![238-0-3-5-6-7-F.png](favorites/238-0-3-5-6-7-F.png)
![252-0-D-6-5-2-3.png](favorites/252-0-D-6-5-2-3.png)
![261-7-6-A-6-F-C-7-6.png](favorites/261-7-6-A-6-F-C-7-6.png)
![290-2-D-6-5-2-3.png](favorites/290-2-D-6-5-2-3.png)
![291-F-E-D-B-5-F-F-2.png](favorites/291-F-E-D-B-5-F-F-2.png)
![300-8-D-6-5-2-2-3.png](favorites/300-8-D-6-5-2-2-3.png)
![332-1-D-B-F-F-2.png](favorites/332-1-D-B-F-F-2.png)
![333-5-3-D-6-5-2-2-3.png](favorites/333-5-3-D-6-5-2-2-3.png)
![34-1-A-3-5-6-2-7-F.png](favorites/34-1-A-3-5-6-2-7-F.png)
![34-C-D-6-5-5-2-3.png](favorites/34-C-D-6-5-5-2-3.png)
![360-B-0-5-5-5-C.png](favorites/360-B-0-5-5-5-C.png)
![454-8-3-5-6-7-F.png](favorites/454-8-3-5-6-7-F.png)
![461-B-0-5-5-5-C.png](favorites/461-B-0-5-5-5-C.png)
![467-3-0-5-5-5-C.png](favorites/467-3-0-5-5-5-C.png)
![468-6-D-6-5-2-3.png](favorites/468-6-D-6-5-2-3.png)
![47-1-D-6-5-2-2-3.png](favorites/47-1-D-6-5-2-2-3.png)
![487-6-0-5-5-5-C.png](favorites/487-6-0-5-5-5-C.png)
![488-6-D-6-5-2-3.png](favorites/488-6-D-6-5-2-3.png)
![98-5-D-6-5-2-3.png](favorites/98-5-D-6-5-2-3.png)
