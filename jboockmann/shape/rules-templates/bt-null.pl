entry(This) :- node(This), left(This, null), right(This, null), true.
entry(This) :- node(This), left(This, null), right(This, Right), p(Right), true.
entry(This) :- node(This), left(This, Left), right(This, null), p(Left), true.
entry(This) :- node(This), left(This, Left), right(This, Right), p(Right), p(Left), true.
p(This) :- node(This), left(This, null), right(This, null), true.
p(This) :- node(This), left(This, null), right(This, Right), p(Right), true.
p(This) :- node(This), left(This, Left), right(This, null), p(Left), true.
p(This) :- node(This), left(This, Left), right(This, Right), p(Left), p(Right), true.