entry(This) :- node(This), left(This, Left), right(This, Right), p(Right), p(Left), true.
p(This) :- node(This), left(This, This), right(This, This), true.
p(This) :- node(This), left(This, This), right(This, Right), p(Right), true.
p(This) :- node(This), left(This, Left), right(This, This), p(Left), true.