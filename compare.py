class Compare:
    def __init__ (self):
        pass

    def match (self, left, right):
        """Mark the right image the same die/cluster as the left image
        If this is the case in a cluster folder -> both remain in the folder
        If happens in Singles folder -> create a new cluster

        Args:
            left (ImgObj): left image
            right (ImgObj): right image

        Returns:
            None
        """

        return None

    def no_match (self, left, right):
        """Right image not the same die/cluster as the left image
        If this is the case in a cluster folder -> move right image to Singles
        If happens in Singles folder -> both remain in Singles

        Args:
            left (ImgObj): left image
            right (ImgObj): right image

        Returns:
            None
        """

        return None

    def best_image (self, left, right):
        """Make the right image the best image of its cluster
        If the left image belong to the same cluster, revoke its status as best_image.
        By default, the first image of a cluster is the best image.
        The image on the left is always the best image of its cluster

        Args:
            left (ImgObj): left image
            right (ImgObj): right image

        Returns:
            None
        """

        return None

    def identical (self, left, right):
        """Mark the left and right images identical or not

        Args:
            left (ImgObj): left image
            right (ImgObj): right image

        Returns:
            bool: True for identical; False for not identical
        """
        return None