-- warmup.

data Tree a = Branch a (Tree a) (Tree a)
            | Leaf
    deriving (Show, Ord, Eq)

traps :: String -> Tree String
traps s = Branch s (traps $ s ++ "a") (traps $ "b" ++ s)

takeTree :: Integer -> Tree a -> [a]
takeTree 0 (Branch x _ _) = [x]
takeTree _ Leaf = []
takeTree n (Branch x lhs rhs) = [x] ++ (takeTree (n-1) lhs) ++ (takeTree (n-1) rhs)

-- utility function

sentencify a = "There was" ++ (foldl (\x a -> x ++ " " ++ a) "" a) ++ "."

--
-- ================================================================
--

-- Now for something more grammar-like.

--   Sentence ::= "There was" Contents ".".
--   Contents ::= Thing ["and" Contents].
--   Thing    ::= "a box containing" Contents
--              | "a rabbit".


data Contents = Single Thing
              | Both Thing Contents
    deriving (Ord, Eq, Show)

data Thing    = Box Contents
              | Rabbit
    deriving (Ord, Eq, Show)


takeContents :: Integer -> Contents -> [String]

takeContents 0 _ = ["some stuff"]
takeContents n (Single t) = takeThing (n-1) t
takeContents n (Both t c) = (takeThing (n-1) t) ++ ["and"] ++ (takeContents (n-1) c)

takeThing :: Integer -> Thing -> [String]

takeThing 0 _ = ["something"]
takeThing n (Box c) = ["a", "box", "containing"] ++ takeContents (n-1) c
takeThing n Rabbit = ["a", "rabbit"]

-- an infinite nest of boxes.

lots1 = Single lots1' where lots1' = Box lots1

-- a box containing an infinite number of rabbits

lots2 = Single (Box lots2') where lots2' = Both Rabbit lots2'

-- a box containing a rabbit and a similar box

lots3 = Single (Box (Both Rabbit lots3))

-- a box containing a similar box and a rabbit.

lots4 = Single box4 where box4 = Box (Both box4 (Single Rabbit))

-- two kinds of boxes containing each other

lots5 = Single boxA
    where
        boxA = Box (Both Rabbit (Single boxB))
        boxB = Box (Single boxA)
