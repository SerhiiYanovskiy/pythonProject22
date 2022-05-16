from google_ import GoogleSheet
from parss import get_usp, get_fedex, get_usps



def main():
    gs = GoogleSheet()
    range = 'testlist!A2:C2000'
    res = gs.read(range)
    for elem in res:
        if elem[1] == "UPS":
            new = get_usp(elem[0])
            elem[2] = str(new)
        elif elem[1] == "FedEx":
            new = get_fedex(elem[0])
            elem[2] = new
        elif elem[1] == "USPS":
            new = get_usps(elem[0])
            elem[2] = new
        else:
            continue

    gs.update(range, res)


if __name__ == "__main__":
    main()

