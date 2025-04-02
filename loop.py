users = {'name': 'ebenezer', 'age': 23, 'nationality': 'Ghannain'}


newusers = {}

for u, desc in users.items():
    if desc != 'ebenezer':
        newusers[u] = desc
        
     

list_user = 300


match list_user:
    case 200:
        print(newusers)
        
    case 100:
        print('User not found')
        
    case _:
        print('Invalid input')
        
        
        
def getNames(*,a, names=None):
    if names is None:
        names = []
    names.append(a)
    
    print(names)
    
    
getNames(a='ebenezer')
getNames('Kate')
getNames('Doreen')